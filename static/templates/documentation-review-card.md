# Documentation task review card

Use this card on one page at a time. A check only passes when the rendered page shows the evidence a reader needs.

## 1. Name the task

- **Reader:** Who is this page for?
- **Starting state:** What do they already have?
- **Task:** What can they complete after reading?
- **Success state:** What command output, response, screen, or state proves it worked?

## 2. Put the risky state beside the action

For every action that can fail, record:

| Action | Failure the reader can recognize | Diagnostic | Safe recovery | Do not retry when |
| --- | --- | --- | --- | --- |
| | | | | |

A failure note belongs beside the step when the answer changes how the reader implements it.

## 3. Make limits observable

| Limited resource | Signal the client can inspect | Exhaustion response | Next action | Owner |
| --- | --- | --- | --- | --- |
| | | | | |

Do not publish a limit warning that leaves the reader unable to identify remaining capacity or the recovery boundary.

## 4. Assign page ownership

- **This page owns:**
- **Link to for prerequisites:**
- **Link to for stable reference detail:**
- **Link to for recovery:**
- **Pages that must not repeat this task:**

## Release check

- The exact procedure has been run from the documented starting state.
- Each step has an observable success state.
- Errors, retries, and limits describe a safe boundary.
- The rendered page, links, metadata, and narrow layout have been checked.
- A named owner knows which product or interface change should trigger review.
