---
category: ai-engineering
date: '2026-04-25'
description: Lambda calculus exposes substitution, scope, and composition errors in
  AI outputs through problems with mechanically checkable answers.
slug: lambda-calculus-ai
status: published
work_note: 'I use problems with checkable answers on this page because a model''s fluent explanation proves nothing by itself. For the technical writing I do for AI companies, see [my portfolio](/portfolio/).'
title: Lambda Calculus as an AI Reasoning Exercise
updated: 2026-11-17
---

Ask a model to reduce `(λx.λy.x) y` and there is one right answer, a function that ignores its input and returns the outer `y`. Lambda calculus works as an AI reasoning exercise because a hundred lines of Python can check that answer, which is why I prefer it to asking a model to explain its reasoning.

The same property carries far larger work. DeepMind's [AlphaProof Code announcement](https://deepmind.google/blog/introducing-alphaproof-code/) of November 10 describes agents that wrote "over six million lines of Lean" to verify Signal's protocol code, and rests the result on one sentence: "Every proof is checked by Lean to verify the agents' work."

An explanation can be fluent and wrong, and a normal form is right or it isn't.

## What does lambda calculus test in a model?

It tests whether the model can keep track of which variable is bound where while it substitutes one expression into another. The whole language is variables, functions written `λx.body`, and application, so there is no library knowledge to recall and little to pattern-match.

A reduction step replaces a function's parameter with its argument. `(λx.x) y` becomes `y`, and larger expressions repeat that step until none applies, which is called reaching normal form.

The skill is narrow, and it is one that agent work depends on. An [agent loop](/articles/agent-loop-anatomy/) passes a tool result into the next step the way a reduction passes an argument into a body, and losing track of which value is which is a failure in both.

## How do you check an answer mechanically?

Run the expression through a reducer and compare normal forms.

The reducer here parses lambda terms and reduces the leftmost outermost application first. It renames variables to avoid capture and stops after 50 steps.

```python
"""Normal-order beta reduction for untyped lambda calculus, with a step limit."""
import itertools
import re

fresh = (f"v{i}" for i in itertools.count(1))


def parse(text):
    tokens = re.findall(r"[λ\\().]|[A-Za-z_][A-Za-z0-9_']*", text)
    pos = 0

    def term():
        nonlocal pos
        parts = []
        while pos < len(tokens) and tokens[pos] != ")":
            parts.append(atom())
        result = parts[0]
        for part in parts[1:]:
            result = ("app", result, part)
        return result

    def atom():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token in "λ\\":
            name = tokens[pos]
            pos += 2  # the variable and the dot
            return ("lam", name, term())
        if token == "(":
            inner = term()
            pos += 1  # the closing parenthesis
            return inner
        return ("var", token)

    return term()


def free(t):
    if t[0] == "var":
        return {t[1]}
    if t[0] == "lam":
        return free(t[2]) - {t[1]}
    return free(t[1]) | free(t[2])


def substitute(t, name, value):
    if t[0] == "var":
        return value if t[1] == name else t
    if t[0] == "app":
        return ("app", substitute(t[1], name, value), substitute(t[2], name, value))
    bound, body = t[1], t[2]
    if bound == name:
        return t
    if bound in free(value):  # rename so the argument's variable is not captured
        renamed = next(fresh)
        body = substitute(body, bound, ("var", renamed))
        bound = renamed
    return ("lam", bound, substitute(body, name, value))


def step(t):
    """One leftmost-outermost reduction, or None if t is in normal form."""
    if t[0] == "app":
        if t[1][0] == "lam":
            return substitute(t[1][2], t[1][1], t[2])
        left = step(t[1])
        if left is not None:
            return ("app", left, t[2])
        right = step(t[2])
        return None if right is None else ("app", t[1], right)
    if t[0] == "lam":
        body = step(t[2])
        return None if body is None else ("lam", t[1], body)
    return None


def show(t):
    if t[0] == "var":
        return t[1]
    if t[0] == "lam":
        return f"λ{t[1]}.{show(t[2])}"
    left = show(t[1]) if t[1][0] != "lam" else f"({show(t[1])})"
    right = show(t[2]) if t[2][0] == "var" else f"({show(t[2])})"
    return f"{left} {right}"


def normalize(text, limit=50):
    t, steps = parse(text), 0
    while steps < limit:
        nxt = step(t)
        if nxt is None:
            return f"{show(t)}   ({steps} steps)"
        t, steps = nxt, steps + 1
    return f"no normal form within {limit} steps"


for expression in [
    "(λx.x) y",
    "((λf.λx.f x) (λy.y)) z",
    "(λf.λx.f (f x)) (λy.λz.z)",
    "(λx.λy.x) y",
    "(λx.x x) (λx.x x)",
]:
    print(f"{expression:<28} -> {normalize(expression)}")
```

Each line from `python3 reduce.py` is an expression and its normal form.

```text
(λx.x) y                     -> y   (1 steps)
((λf.λx.f x) (λy.y)) z       -> z   (3 steps)
(λf.λx.f (f x)) (λy.λz.z)    -> λx.λz.z   (2 steps)
(λx.λy.x) y                  -> λv1.y   (1 steps)
(λx.x x) (λx.x x)            -> no normal form within 50 steps
```

The first, second and last lines are the tiers the figure below draws. The fourth is the case that catches careless substitution.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/lambda-calculus-ai/reduction-tiers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/lambda-calculus-ai/reduction-tiers.narrow.svg" width="288" height="432"><img class="np-has-narrow" src="/static/images/diagrams/lambda-calculus-ai/reduction-tiers.svg" width="720" height="528" alt="Three difficulty tiers for beta reduction. A direct application reaches its normal form in one substitution. A chained application takes more than one step, keeping its bindings, before it reaches a normal form. The Omega combinator reduces to itself forever, so the correct answer is to detect that it has no normal form rather than invent a terminating one." loading="lazy" decoding="async"></picture></a>
  <figcaption>The third tier separates a system that notices Ω never finishes from one that writes a tidy answer for it.</figcaption>
</figure>

## Which problems separate careful substitution from pattern matching?

The fourth and fifth do, more than the tiers above them. The argument in `(λx.λy.x) y` is named `y` and so is the inner parameter, and a naive substitution gives `λy.y`, the identity function.

The right answer is a function that ignores its input and returns the outer `y`, which the reducer writes as `λv1.y` after renaming. A model that answers `λy.y` has made the same mistake as code that shadows a variable.

`(λx.x x) (λx.x x)` reduces to itself forever. The correct response is that it has no normal form, and a tidy finite answer is a sign the model produced what an answer usually looks like.

## What can't this exercise tell you?

It can't tell you how a model performs on anything except substitution and scope. Good results here say nothing about tool use or planning, and the [agent failure patterns](/articles/ai-agent-failures/) I cover elsewhere have other causes.

No model results are reported here. The reducer was run, as shown above, and no set of models has been put through the problems for this page, so treat it as a method with a working checker and no leaderboard.

The AlphaProof post marks the same boundary at its own scale. A proof checker confirms that code meets a specification, and the post has people deciding what to prove: "human experts work with AI to decide what to prove, and a group of AI agents does it."

## How do you turn it into an evaluation?

Generate expressions, ask each model for the normal form, and score with the reducer. A few details make the scores mean something.

- Compare answers after renaming bound variables, since `λa.a` and `λb.b` are the same function and the script above doesn't normalize names for you.
- Include expressions with no normal form and accept only an answer that says so.
- Publish the expressions and the raw outputs with the scores, so a reader can rerun the check.

Record the kind of error as well as the count. A capture error and a wrong claim of termination point at different weaknesses, and the [error handling guide](/articles/agent-error-handling/) covers what the second looks like in a running agent.

Binding matters wherever a system carries values across steps, which includes the [memory systems](/articles/agent-memory-2026/) agents use between sessions. A reduction test is a cheap first filter before the expensive ones.
