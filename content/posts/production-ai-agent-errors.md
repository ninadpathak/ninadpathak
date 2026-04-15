---
title: "What Nobody Tells You About Error Handling in Production AI Agents"
date: 2026-04-16
description: "Hard-won lessons from running AI agents in production: the error patterns that actually break systems, and the patterns that fix them."
tags: [ai, devtools, backend, sre]
status: published
---

After running AI agents in production for two years, I can tell you that the error handling is the difference between a system that survives contact with reality and one that falls over the moment something goes slightly wrong. The glamorous part of AI agents is the reasoning and tool use. The unglamorous part, the part that keeps your on-call phone from lighting up at 2 AM, is error handling.

I have seen agents loop indefinitely because a tool returned an unexpected format. I have seen agents silently fail to complete multi-step workflows because a downstream API was throttled for 200 milliseconds. I have seen agents corrupt state because they retried a non-idempotent operation without checking whether it had already succeeded. These are not theoretical problems. Every team I know that runs agents in production has hit some version of all of them.

This article is about the error patterns that actually break AI agents in production, and the concrete patterns that fix them. I am focusing on agents built on LLMs that use tools to interact with external systems. That covers the majority of production agents I have encountered.

## The Fundamental Problem: Agents Are State Machines Nobody Designed

The first thing to understand is that an AI agent is a state machine, even though nobody writes it that way. An agent has a current state (the conversation history, the tool results so far, any scratchpad memory), it receives inputs (user messages, tool responses, time), and it transitions to new states by deciding which tool to call next. When you think about it this way, error handling becomes a state machine design problem, which is a domain where software engineers have decades of established practice.

The problem is that most agent implementations do not think about it this way at all. The agent loop looks something like this: receive a message, call the LLM, parse the tool call, execute the tool, append the result, repeat. Error handling typically means wrapping the tool execution in a try-except that logs the error and tells the LLM something went wrong. That is insufficient, and here is why.

When a tool call fails, the agent's state is now inconsistent. The LLM decided to call that tool based on everything it knew up to that point. If the tool call fails and you just return an error message, the LLM has to decide what to do with that information. Sometimes it recovers gracefully. Often it tries the same tool again with slightly different arguments. Occasionally it calls a completely different tool that assumes the first tool succeeded, and now you have a cascading failure that is hard to debug.

The core issue is that error handling in agents requires you to think about which states are recoverable and which are not, and then design explicit transitions for both cases.

## Pattern 1: Classify Errors Before Deciding What to Do

Not all errors are equal. The single most impactful change you can make to your agent's error handling is to classify errors into categories before deciding how to respond. I use three categories that cover the vast majority of cases.

**Transient errors** are temporary. A network timeout, a rate limit, a server that is briefly overloaded. These are candidates for retry, but retries must be handled carefully, which I will get to. **Permanent errors** are things that will not resolve on their own. A missing parameter, an invalid API key, a resource that does not exist. Retrying these wastes time and risks cascading failures. **Ambiguous errors** are the tricky ones. The request timed out. Did the server process it or not? The API returned a 500. Was it a data corruption or a load issue? These require idempotency-aware retry logic.

Here is a practical classification function that I use as a starting point.

```python
from enum import Enum
from typing import Union
import httpx

class ErrorCategory(Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    AMBIGUOUS = "ambiguous"

def classify_error(error: Exception, response: Union[httpx.Response, None] = None) -> ErrorCategory:
    if isinstance(error, httpx.TimeoutException):
        return ErrorCategory.AMBIGUOUS
    if isinstance(error, httpx.ConnectError):
        return ErrorCategory.TRANSIENT
    if isinstance(error, httpx.HTTPStatusError):
        if response is not None:
            status = response.status_code
            if status == 429:
                return ErrorCategory.TRANSIENT
            if status == 401 or status == 403:
                return ErrorCategory.PERMANENT
            if status == 404:
                return ErrorCategory.PERMANENT
            if 500 <= status < 600:
                return ErrorCategory.TRANSIENT
        return ErrorCategory.AMBIGUOUS
    if isinstance(error, ValueError):
        return ErrorCategory.PERMANENT
    return ErrorCategory.AMBIGUOUS
```

This is a simplified version. Your production code will need to handle your specific error types, but the principle is the same. Classify before you react.

## Pattern 2: Retry with Exponential Backoff and Jitter, But Only for the Right Errors

Once you have classified your error, retry logic follows naturally. Transient errors should be retried with backoff. Permanent errors should not be retried at all. Ambiguous errors require idempotency-aware retry logic, which is the hardest part.

For backoff, the standard approach is exponential backoff with jitter. The formula is `min(base * (2 ** attempt), max_delay) + random_jitter`. A base of 1 second and a max delay of 60 seconds works for most APIs.

```python
import random
import time

def retry_with_backoff(func, max_attempts=5, base=1.0, max_delay=60.0):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            category = classify_error(e)
            if category == ErrorCategory.PERMANENT:
                raise
            if attempt == max_attempts - 1:
                raise
            delay = min(base * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            time.sleep(delay + jitter)
```

The jitter is important. Without it, all clients that hit a transient failure will retry at the same time, which can turn a brief outage into a sustained thundering herd problem.

Now for the hard case: ambiguous errors. If a request to your payment API times out, you do not know whether the server processed the charge or not. Retrying immediately could charge the customer twice. The standard solution is idempotency keys. Generate a unique key for the operation, send it with the request, and if the request times out, retry with the same key. The server stores the result keyed by the idempotency key and returns the cached result on duplicate requests.

```python
import uuid

def call_with_idempotency(func, max_attempts=3):
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}
    for attempt in range(max_attempts):
        try:
            return func(headers=headers)
        except Exception as e:
            category = classify_error(e)
            if category != ErrorCategory.AMBIGUOUS:
                raise
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)
```

Not every API supports idempotency keys. For those that do not, you have to decide whether the cost of a potential duplicate is worth the cost of a failure. For payments, it is almost never worth the risk. For a background enrichment job, it might be fine to occasionally run twice. Know your blast radius.

## Pattern 3: Circuit Breakers Prevent Cascading Failures

Retry logic helps when failures are rare. When failures become common, retries make things worse. Every client that keeps hammering a failing service adds load, which slows the service more, which causes more timeouts, which causes more retries. The circuit breaker pattern breaks this loop.

The idea is simple. Track the failure rate for each downstream service. If the failure rate exceeds a threshold, "open" the circuit: stop making requests to that service for a period of time and immediately return an error to the caller. After the timeout, allow a single request through. If it succeeds, "close" the circuit and restore normal operation. If it fails, open the circuit again.

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=0.5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.total_calls = 0

    def call(self, func):
        if self.state == CircuitState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is open")
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
        self.total_calls += 1

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.total_calls += 1
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.total_calls > 10:
            failure_rate = self.failure_count / self.total_calls
            if failure_rate > self.failure_threshold:
                self.state = CircuitState.OPEN
```

This is a simplified version. Production circuit breakers also need to handle partial failures (where the downstream returned a response but it was an error response), sliding window failure tracking instead of simple counters, and programmatic reset APIs. The Pybreaker library handles these cases well if you are working in Python.

The important insight is that circuit breakers protect your agent from downstream services, but they also protect downstream services from your agent. When a service is struggling, the worst thing you can do is keep sending it requests. Circuit breakers are how you stop.

## Pattern 4: Structured Error Context for the LLM

When a tool fails and you tell the LLM, what you tell it matters enormously. A raw exception message is almost useless. The LLM does not know which tool was being called, whether this is a common failure mode for this tool, or whether there is a recovery path.

I use a structured error context object that gets appended to the agent's context alongside the error.

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ToolErrorContext:
    tool_name: str
    error_type: str
    error_message: str
    is_retryable: bool
    retry_after_seconds: Optional[float] = None
    suggested_alternatives: Optional[list[str]] = None
    incident_id: Optional[str] = None

def format_error_for_llm(error: ToolErrorContext) -> str:
    parts = [
        f"Tool '{error.tool_name}' failed.",
        f"Error type: {error.error_type}.",
        f"Message: {error.error_message}.",
    ]
    if error.is_retryable:
        parts.append("This error is retryable.")
        if error.retry_after_seconds:
            parts.append(f"Recommended wait: {error.retry_after_seconds} seconds.")
    else:
        parts.append("This error is not retryable.")
    if error.suggested_alternatives:
        parts.append(f"Consider alternatives: {', '.join(error.suggested_alternatives)}.")
    if error.incident_id:
        parts.append(f"Reference: {error.incident_id}.")
    return " ".join(parts)
```

This is what the LLM sees when a tool fails. It knows the tool name, the error type, whether to retry, how long to wait, and what alternatives exist. With this context, the LLM can make an informed decision about whether to retry, try a different tool, or escalate to the user. Without it, the LLM is guessing.

The `suggested_alternatives` field is particularly useful. If your primary search tool is rate-limited, you can suggest an alternative search endpoint. If the database is unavailable, you can suggest the cache as a fallback. You are encoding domain knowledge into the error context so the LLM does not have to rediscover it every time.

## Pattern 5: Timeout Everything, and Set the Right Values

LLM calls are one of the most common sources of unexpected hangs in agent systems. The default timeout for most HTTP clients is either very long (30 seconds to no timeout) or undefined. For LLM API calls, you need an explicit timeout that accounts for both the model's latency and the request's complexity.

For most gpt-4 class models, 60 seconds is a reasonable timeout for a single turn. For o1 class models that do internal reasoning, 120 seconds is more appropriate. For streaming responses, you need a timeout for the first token and a separate timeout for the total response.

The key insight is that a timeout is not a failure, it is an error category. You need to decide what a timeout means for your agent. Does it mean the model is slow (retry)? Does it mean the model is stuck in a loop (do not retry)? Does it mean the request is too complex (break it into smaller steps)? Your timeout handling should be informed by which of these is most likely.

```python
async def call_llm_with_timeout(messages, timeout=60):
    async with asyncio.timeout(timeout):
        return await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
```

For tool calls, the timeout depends on the tool. A search API call might need 10 seconds. A database query might need 5 seconds. A file read might need 2 seconds. Set these explicitly based on what you know about your tools, not based on defaults.

## Pattern 6: Graceful Degradation Over Hard Failures

Production agents should have a concept of "good enough" responses. If your agent is designed to search three sources and synthesize the results, and one source is unavailable, it should still search the other two and note that one source failed. This is graceful degradation.

Hard failures happen when your agent has a single point of failure with no fallback. If the LLM call fails, the whole agent fails. If one tool fails, the whole workflow fails. Graceful degradation means designing your agent with fallbacks from the start.

The implementation pattern I use is a required-vs-optional distinction for tools. When defining the agent's available tools, mark some as required and others as optional. If a required tool fails, the agent should escalate to the user or return an error state. If an optional tool fails, the agent should continue without it and note the failure in its response.

```python
TOOL_DEFINITIONS = [
    {"name": "search", "required": True},
    {"name": "calculate", "required": True},
    {"name": "fetch_metadata", "required": False},
    {"name": "log_event", "required": False},
]

def execute_tools(tool_calls, required_tool_names):
    results = {}
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        try:
            results[tool_name] = execute(tool_call)
        except Exception as e:
            if tool_name in required_tool_names:
                raise
            results[tool_name] = {"error": str(e), "status": "failed"}
    return results
```

This is a simplified version. In practice, you need to propagate these partial failures through the agent's context so the LLM knows what happened and can respond appropriately.

## What Actually Matters in Production

After two years of running agents in production, here is what I have learned. Error handling is not an afterthought. It is a first-class design concern that you need to think about before you deploy, not after your first incident.

The patterns that matter most are the ones that prevent cascading failures: circuit breakers, timeouts, and idempotency-aware retry logic. The patterns that matter most for debugging are structured error context and classification. The patterns that matter most for reliability are graceful degradation and required-vs-optional tool designation.

One more thing. Test your error handling. I do not mean unit tests for your error handling functions, though those are fine. I mean inject failures into your system in staging and watch what happens. Disable your LLM. Return 500s from your tools. Slow down your database. Your agent should handle all of these gracefully. If it does not, you have work to do before production.

The agents that survive contact with reality are not the ones with the most sophisticated reasoning. They are the ones that fail gracefully, recover quickly, and give their users useful information when things go wrong. That is what error handling is for.
