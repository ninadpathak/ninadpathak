---
title: "What Nobody Tells You About Error Handling in Production AI Agents"
date: 2026-04-16
description: "Hard-won lessons from running AI agents in production: the error patterns that actually break systems, and the patterns that fix them."
tags: [ai, devtools, backend, sre]
status: published
---

After two years of running AI agents in production, here is what I know: error handling is the difference between a system that survives reality and one that falls over the moment something goes wrong. The glamorous part is reasoning and tool use. The unglamorous part, the part that keeps your on-call phone from lighting up at 2 AM, is error handling.

The failures are predictable. Agents loop indefinitely because a tool returned an unexpected format. Agents silently drop steps because a downstream API throttled for 200 milliseconds. Agents corrupt state because they retried a non-idempotent operation without checking whether it already succeeded. Every team I know running agents has hit some version of all three. I have hit all three myself, usually at the worst possible time.

This is about the error patterns that actually break agents in production, and the concrete patterns that fix them. I am focusing on LLM-based agents that use tools to interact with external systems. That covers the majority of production agents I have encountered.

## The core problem: agents are undefined state machines

Most agent implementations look like this: receive message, call LLM, parse tool call, execute tool, append result, repeat. Error handling is a try-except that logs the error and tells the LLM something went wrong.

This fails because tool failure leaves the agent in an undefined state. The LLM decided to call that tool based on everything it knew. Returning an error string leaves the LLM to improvise recovery. Sometimes it recovers. Often it retries the same tool with slightly different arguments. Occasionally it calls a completely different tool that assumes the first succeeded, and now you have a cascading failure that is hard to trace back.

The fix is to classify errors before deciding how to respond.

## Classify errors first

Three categories cover most cases.

**Transient**: timeouts, rate limits, overloaded servers. These are candidates for retry with backoff.

**Permanent**: missing parameters, invalid API keys, nonexistent resources. Retrying these wastes time and causes cascading failures. Fail fast.

**Ambiguous**: the request timed out, but you do not know if the server processed it. This is the hardest category. It requires idempotency-aware retry logic.

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

This five-minute classification function has saved me more debugging time than anything else in my agent infrastructure.

## Idempotent tool design

Agents retry. When a tool call fails ambiguously, the agent calls it again. If the tool is not idempotent, the retry causes duplicate side effects.

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

For tools that cannot be made naturally idempotent, use a deduplication layer.

```python
def execute_with_deduplication(tool_fn, operation_id: str, **kwargs):
    if cache.has(operation_id):
        return cache.get(operation_id)
    result = tool_fn(**kwargs)
    cache.set(operation_id, result, ttl=3600)
    return result
```

I have seen this prevent duplicate payment processing twice. It is not optional.

## Explicit state transitions

When a tool fails, the agent needs an explicit recovery path, not just an error string. The code decides the recovery strategy. The LLM receives a clean state transition and acts accordingly.

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

Agents running dozens of steps need state persistence. Without it, a failure at step 40 restarts from step 1. This is the most demoralizing thing to debug at 1 AM.

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

LLM API timeouts are ambiguous. The request might have been processed. Set conservative timeouts and use idempotency keys.

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

**Context window exhaustion**: the agent accumulates tool results until the context is full. Set a hard limit on total tool call history and fail explicitly when approaching the limit.

**Tool schema drift**: the LLM calls a tool with parameters that match an older version of the schema. Version your tool schemas and validate inputs against the expected version before executing.

**Partial failure in parallel tool calls**: the agent calls multiple tools simultaneously. Some succeed, some fail. Track each independently and do not assume all-or-nothing semantics.

**Ambiguous timeouts**: a timeout fires but the server might have processed the request. If the operation is not idempotent, you risk duplication. Always use idempotency keys for non-idempotent operations.

**Observability gaps**: without structured logs of tool inputs and outputs, debugging a failed agent run is archaeology. Log every tool call with its input, output, latency, and error.

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

Classify errors before deciding how to respond. Returning raw errors to the LLM is not error handling.

Design tools to be idempotent or use a deduplication layer. Non-idempotent tools will be called twice. I have the Stripe charge receipts to prove it.

Checkpoint long-horizon tasks. A failure at step 40 that restarts from step 1 is not acceptable.

Set explicit timeout and retry policies. Default timeouts are not tuned for your use case.

Log every tool call with inputs, outputs, latency, and errors. Without observability, debugging is archaeology.

These patterns apply regardless of which LLM or framework you use. The error modes are the same across providers. The fixes are the same too.
