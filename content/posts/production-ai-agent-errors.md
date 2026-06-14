---
title: "What Nobody Tells You About Error Handling in Production AI Agents"
date: 2026-04-16
description: "Hard-won lessons from running AI agents in production: the error patterns that actually break systems, and the patterns that fix them."
tags: [ai, devtools, backend, sre]
status: published
---

Two years of running AI agents in production taught me that error handling separates a system that survives reality from one that falls over the moment something goes wrong. Reasoning and tool use get all the attention. Error handling, the part that keeps your on-call phone quiet at 2 AM, gets almost none.

The failures are predictable, and they line up with [the broader pattern of why agents keep failing in production](/blog/why-ai-agents-keep-failing-in-production/). An agent loops forever because a tool returned JSON wrapped in a markdown code fence and the parser choked. Another silently drops a step because a downstream API throttled for 200 milliseconds and the agent treated the empty response as "done." A third corrupts state because it retried a charge endpoint without checking whether the first attempt had already gone through. I have hit all three myself, usually at the worst possible time.

What follows are the error patterns that actually break agents in production, and the concrete patterns that fix them. My focus is LLM-based agents that call tools to interact with external systems, which covers the majority of production agents I have run into.

## The core problem: agents are undefined state machines

Nearly every agent implementation I have seen looks like this: receive message, call LLM, parse tool call, execute tool, append result, repeat. Error handling is a try-except that logs the error and tells the LLM something went wrong.

Tool failure leaves the agent in an undefined state, and that is where things fall apart. The LLM picked that tool based on everything it knew at the time. Hand it back a raw error string and it improvises a recovery. Sometimes it recovers cleanly. More often it retries the same tool with the arguments nudged slightly, say swapping `user_id` for `userId` because the error mentioned a missing field. Occasionally it moves on to a different tool that assumes the first one succeeded, like calling `send_invoice` after `create_charge` actually failed, and now you have a cascading failure that takes an hour to trace back.

Classifying errors before you decide how to respond is what breaks the cycle. A short classification function, the kind you can write over a coffee, has saved me more debugging time than anything else in my agent infrastructure.

## Classify errors first

Three categories cover most cases.

**Transient**: timeouts, rate limits, overloaded servers. These are candidates for retry with backoff.

**Permanent**: missing parameters, invalid API keys, nonexistent resources. Retrying these wastes time and causes cascading failures. Fail fast.

**Ambiguous**: the request timed out, and you have no idea whether the server processed it. Picture submitting a payment, getting no response, and not knowing if the customer was charged. That uncertainty is what makes this category demand idempotency-aware retry logic.

```python
from enum import Enum
import httpx

class ErrorCategory(Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    AMBIGUOUS = "ambiguous"

def classify_error(error: Exception, response: httpx.Response = None) -> ErrorCategory:
    if isinstance(error, httpx.TimeoutException):
        return ErrorCategory.AMBIGUOUS
    if isinstance(error, httpx.ConnectError):
        return ErrorCategory.TRANSIENT
    if isinstance(error, httpx.HTTPStatusError) and response:
        if response.status_code in (429, 502, 503, 504):
            return ErrorCategory.TRANSIENT
        if response.status_code in (400, 401, 403, 404):
            return ErrorCategory.PERMANENT
        if response.status_code >= 500:
            return ErrorCategory.AMBIGUOUS
    return ErrorCategory.AMBIGUOUS
```

## Idempotent tool design

Agents retry. When a tool call fails ambiguously, the agent calls it again, and a tool that is not idempotent turns that retry into duplicate side effects: two welcome emails, two records, two charges.

Design tools to be safe to call twice.

```python
# Bad: creates a new record every time
def create_user(email: str) -> dict:
    return api.post("/users", {"email": email})

# Good: checks for existing user first
def create_user(email: str) -> dict:
    existing = api.get(f"/users?email={email}")
    if existing:
        return existing
    return api.post("/users", {"email": email})
```

When a tool cannot be made naturally idempotent, a deduplication layer keyed on the operation ID does the job. The dedup cache works like a coat check ticket: the first call hands back a stub, and every later call with the same ticket gets the original result instead of running the operation again. I have watched this exact pattern stop a retrying agent from double-charging a customer, which is reason enough to treat it as mandatory rather than nice-to-have.

```python
def execute_with_deduplication(tool_fn, operation_id: str, **kwargs):
    if cache.has(operation_id):
        return cache.get(operation_id)
    result = tool_fn(**kwargs)
    cache.set(operation_id, result, ttl=3600)
    return result
```

## Explicit state transitions

When a tool fails, the agent needs an explicit recovery path rather than a raw error string to puzzle over. Your code, not the model, decides the recovery strategy. The LLM then receives a clean state transition, something like "retrying, attempt 2 of 3," and acts on that instead of guessing.

```python
class AgentState(Enum):
    RUNNING = "running"
    WAITING_ON_RETRY = "waiting_on_retry"
    RECOVERING = "recovering"
    FAILED = "failed"

def handle_tool_error(state: AgentState, error: Exception, context: dict) -> AgentState:
    category = classify_error(error)
    if category == ErrorCategory.PERMANENT:
        context["failure_reason"] = str(error)
        return AgentState.FAILED
    if category == ErrorCategory.TRANSIENT:
        if context.get("retry_count", 0) >= 3:
            context["failure_reason"] = f"Max retries exceeded: {error}"
            return AgentState.FAILED
        context["retry_count"] = context.get("retry_count", 0) + 1
        return AgentState.WAITING_ON_RETRY
    # Ambiguous: checkpoint before retry
    checkpoint_state(context)
    return AgentState.RECOVERING
```

## Checkpointing for long-horizon tasks

Agents running dozens of steps need state persistence, which is one of the core responsibilities of a well-designed [agent harness, the infrastructure layer your agent actually needs](/blog/agent-harnesses/). Lose that, and a failure at step 40 of a data migration restarts from step 1, redoing 39 steps that already committed. Few things are more demoralizing to debug at 1 AM than watching an agent cheerfully redo work it already finished.

```python
import json
from datetime import datetime
import os

def checkpoint_state(context: dict):
    checkpoint = {
        "step": context.get("current_step"),
        "history": context.get("message_history"),
        "tool_results": context.get("tool_results"),
        "checkpointed_at": datetime.utcnow().isoformat()
    }
    path = f"/tmp/agent_checkpoint_{context['task_id']}.json"
    with open(path, "w") as f:
        json.dump(checkpoint, f)

def restore_if_exists(task_id: str) -> dict | None:
    path = f"/tmp/agent_checkpoint_{task_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None
```

Write checkpoints after each successful step. On restart, restore from the most recent checkpoint before retrying.

## Timeout strategy

LLM API timeouts sit squarely in the ambiguous bucket, since a request that times out at the client may still have been processed on the provider's side and billed to you. Set conservative timeouts and pass idempotency keys so a retry collapses onto the same completion instead of generating and charging for a second one.

```python
import httpx

client = httpx.Client(
    timeout=httpx.Timeout(30.0, connect=5.0),
    follow_redirects=True
)

def llm_call_with_idempotency(prompt: str, operation_id: str) -> str:
    headers = {"Idempotency-Key": operation_id}
    response = client.post(
        "https://api.llm.provider/v1/completions",
        json={"prompt": prompt},
        headers=headers
    )
    return response.json()["completion"]
```

## What actually breaks in practice

Five failure modes show up consistently across production incidents.

<div class="visual-wrapper">
  <div class="visual-title">PRODUCTION AGENT ERROR TAXONOMY</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-error-taxonomy.html" title="Taxonomy of production agent failure classes and how each is handled" loading="lazy"></iframe>
  </div>
</div>

**Context window exhaustion**: the agent piles up tool results, say twenty paginated API responses, until the context is full and the next call rejects. Set a hard limit on total tool call history and fail explicitly when you approach it rather than letting the provider error out mid-task.

**Tool schema drift**: the LLM calls a tool with parameters from an older version of the schema, passing `customer` long after you renamed the field to `customer_id`. Version your tool schemas and validate inputs against the expected version before executing.

**Partial failure in parallel tool calls**: the agent fires off five tools at once, three succeed and two fail. Track each one independently and never assume all-or-nothing semantics, because the agent will happily build its next step on the three that worked.

**Ambiguous timeouts**: a timeout fires while the server may have processed the request anyway. Non-idempotent operations then risk duplication, so always attach idempotency keys to them.

**Observability gaps**: without structured logs of tool inputs and outputs, debugging a failed run turns into archaeology, sifting through stack traces to reconstruct what the agent even tried. Log every tool call with its input, output, latency, and error.

```python
def logged_tool_call(tool_name: str, tool_fn, **kwargs):
    start = time.time()
    try:
        result = tool_fn(**kwargs)
        logger.info("tool_call", extra={
            "tool": tool_name,
            "latency_ms": (time.time() - start) * 1000,
            "status": "success",
            "input_params": list(kwargs.keys())
        })
        return result
    except Exception as e:
        logger.error("tool_call", extra={
            "tool": tool_name,
            "latency_ms": (time.time() - start) * 1000,
            "status": "error",
            "error": str(e)
        })
        raise
```

## The non-negotiables

Five things will break your agent in production if you skip them.

Classify errors before deciding how to respond, because returning raw errors to the LLM and hoping it sorts them out is not error handling.

Whether through naturally idempotent design or a deduplication layer, make every tool safe to call twice. Non-idempotent tools get called twice eventually.

Checkpoint long-horizon tasks so a failure at step 40 resumes near step 40. Restarting from step 1 is not acceptable.

Explicit timeout and retry policies matter more than any default the SDK ships with, since those defaults were never tuned for your latency or your cost ceiling.

Log every tool call with inputs, outputs, latency, and errors. Skip the observability and your next debugging session becomes archaeology.

These patterns hold regardless of which LLM or framework you reach for, because the error modes stay the same across providers.
