---
title: "What Nobody Tells You About Error Handling in Production AI Agents"
date: 2026-04-16
description: "The error patterns that actually break AI agents in production, and the patterns that fix them."
tags: [ai, devtools, backend, sre]
status: published
---

AI agents fail in predictable ways. After two years of running them in production, the error patterns are consistent across teams and use cases. This article covers the patterns that actually break systems and the concrete fixes.

The most common failures: agents looping on unexpected tool output, silently dropping steps when APIs throttle, and corrupting state on non-idempotent retries. These are not edge cases. Every team running agents hits all of them.

## The Core Problem: Agents Are Undefined State Machines

Most agent implementations look like this: receive message, call LLM, parse tool call, execute tool, append result, repeat. Error handling is a try-except that logs and tells the LLM something went wrong.

This fails because tool failure leaves the agent in an undefined state. The LLM decided to call that tool based on everything it knew. Returning an error message leaves the LLM to decide what happens next. It might retry the same tool, try a different tool that assumes the first succeeded, or give up entirely. None of these are predictable.

Fix this by classifying errors before deciding how to respond.

## Classify Errors First

Three categories cover most cases.

**Transient**: temporary failures like timeouts, rate limits, overloaded servers. Candidates for retry with backoff.

**Permanent**: missing parameters, invalid API keys, nonexistent resources. Retrying wastes time and causes cascading failures. Fail fast.

**Ambiguous**: timeouts where you do not know if the server processed the request. The hardest category. Requires idempotency-aware retry logic.

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

## Pattern 2: Idempotent Tool Design

Agents retry. When a tool call fails ambiguously, the agent might call it again. If the tool is not idempotent, the retry causes duplicate side effects.

Design tools to be safe to call twice.

```python
# Bad: creates a new record on every call
def create_user(email: str) -> dict:
    return api.post("/users", {"email": email})

# Good: checks if user exists first
def create_user(email: str) -> dict:
    existing = api.get(f"/users?email={email}")
    if existing:
        return existing
    return api.post("/users", {"email": email})
```

For tools that cannot be made idempotent, use a unique operation ID.

```python
def execute_with_deduplication(tool_fn, operation_id: str, **kwargs):
    if cache.has(operation_id):
        return cache.get(operation_id)
    result = tool_fn(**kwargs)
    cache.set(operation_id, result)
    return result
```

## Pattern 3: Explicit State Transitions

When a tool fails, the agent needs an explicit recovery path, not just an error string.

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
    # Ambiguous: checkpoint state before retry
    checkpoint_state(context)
    return AgentState.RECOVERING
```

The LLM does not decide recovery strategy. The code does. The LLM receives a clean state transition and acts accordingly.

## Pattern 4: Checkpointing for Long-Horizon Tasks

Agents that run dozens of steps need state persistence. Without it, a failure at step 30 restarts from step 1.

```python
import json
from datetime import datetime

def checkpoint_state(context: dict):
    checkpoint = {
        "step": context.get("current_step"),
        "history": context.get("message_history"),
        "tool_results": context.get("tool_results"),
        "checkpointed_at": datetime.utcnow().isoformat()
    }
    with open(f"/tmp/agent_checkpoint_{context['task_id']}.json", "w") as f:
        json.dump(checkpoint, f)

def restore_if_exists(task_id: str) -> dict | None:
    path = f"/tmp/agent_checkpoint_{task_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None
```

Write checkpoints after each successful step. On restart, restore from the most recent checkpoint before retrying.

## Pattern 5: Timeout Strategy

LLM API timeouts are ambiguous by definition. The request might have been processed. Set timeouts conservatively and use idempotency keys.

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

## What Actually Breaks in Practice

Based on production incidents across teams:

**Context window exhaustion**: The agent accumulates tool results until the context is full. Set a hard limit on total tool call history and fail explicitly when approaching the limit.

**Tool schema drift**: The LLM calls a tool with parameters that match an older version of the schema. Version your tool schemas and validate inputs against the expected version.

**Partial failure in parallel tool calls**: The agent calls multiple tools simultaneously. Some succeed, some fail. Track each independently and do not assume all-or-nothing.

**Observability gaps**: Without structured logs of tool inputs and outputs, debugging a failed agent run is guesswork. Log every tool call with its input, output, latency, and error.

```python
def logged_tool_call(tool_name: str, tool_fn, **kwargs):
    start = time.time()
    try:
        result = tool_fn(**kwargs)
        logger.info(f"tool_call", extra={
            "tool": tool_name,
            "latency_ms": (time.time() - start) * 1000,
            "status": "success",
            "input_params": list(kwargs.keys())
        })
        return result
    except Exception as e:
        logger.error(f"tool_call", extra={
            "tool": tool_name,
            "latency_ms": (time.time() - start) * 1000,
            "status": "error",
            "error": str(e)
        })
        raise
```

## The Non-Negotiables

Five things will break your agent in production if you skip them.

First, classify errors before deciding how to respond. Returning raw errors to the LLM is not error handling.

Second, design tools to be idempotent or use deduplication. Non-idempotent tools will be called twice.

Third, checkpoint long-horizon tasks. A failure at step 40 that restarts from step 1 is not acceptable.

Fourth, set explicit timeout and retry policies. Do not rely on defaults.

Fifth, log every tool call with inputs, outputs, latency, and errors. Without observability, debugging is archaeology.

These patterns apply regardless of which LLM or framework you use. The error modes are the same across providers.
