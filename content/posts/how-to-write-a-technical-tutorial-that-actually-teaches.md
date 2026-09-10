---
category: technical-documentation
date: 2026-04-02
description: Write a technical tutorial that takes one reader from a clear starting
  point to a tested, useful result.
slug: how-to-write-a-technical-tutorial-that-actually-teaches
status: published
tags:
- technical-writing
- tutorials
- developer-experience
takeaways:
- Choose one reader, one starting state, and one result they can verify.
- Build the working path before writing the explanation around it.
- Use task-based headings, runnable code, and visible checkpoints.
- Test every step in a clean environment before publishing.
title: How to Write a Technical Tutorial That Actually Teaches
updated: 2026-09-10
---

The earlier worked example on this page imported `verifyWebhook` from `@example/webhooks` and celebrated a successful event without supplying the dependency or a command to start the server. Copy that import into a clean directory and the whole performance falls over before a request reaches the handler.

I don't call a page a tutorial because it has numbered steps and cheerful code blocks. A tutorial has to carry one reader from a stated starting point to a result they can see, then survive the obvious ways that path can break.

I use that complete path as the outline. The synthetic fixture below accepts a signed event, rejects altered bytes, and supplies the full source for a clean run.

## Define a reader and a result you can test

Write the starting state before the steps. For this example, the reader can run JavaScript from a terminal and wants to understand what a webhook tutorial must supply.

| Requirement | Check | If it fails |
| --- | --- | --- |
| Node.js 24.18.0, the recorded test version | `node --version` | Use the recorded version before comparing results |
| An extracted copy of the fixture | Confirm `service.mjs`, `webhook.mjs`, and `check.mjs` exist | Extract the complete archive |
| A successful event and a rejected signature | Run `node check.mjs` | Inspect the failing assertion before describing the example as runnable |

The finish line is deliberately bounded: accept an event signed with the fixture's public test value, reject altered bytes, and confirm rejected events were not recorded. Calling this a production webhook system would turn a useful teaching fixture into bullshit.

If the reader only needs a signature field definition, give them reference documentation instead of this build sequence. The [documentation types guide](/articles/types-of-technical-documentation/) separates those jobs.

## Build the tutorial around observable checkpoints

The fixture uses Node's built-in HTTP and cryptography modules to compute a lowercase hexadecimal HMAC-SHA256 digest over the exact request bytes. Removing the unexplained package makes the example self-contained, but also makes the protocol our responsibility to describe.

### Step 1: Create the project from the complete fixture

[Download the writing lab](/static/examples/writing-lab.zip), extract it into an empty directory, and open the `writing-lab` folder in a terminal. The archive contains the implementation and its checks, with no npm dependencies.

```bash
node --version
node check.mjs
```

The recorded runtime is `v24.18.0`. The check ends with `PASS` and closes the servers it creates.

If a file cannot be imported, compare the extracted directory with the archive before installing packages guessed from an error message. Reproduce the earlier omission separately in an empty directory:

```bash
node --input-type=module -e 'import { verifyWebhook } from "@example/webhooks"'
```

The recorded `ERR_MODULE_NOT_FOUND` establishes a missing dependency path in the supplied instructions, not a claim about registry availability. Replacing one unexplained import with another would leave the tutorial's problem intact.

### Step 2: Keep the bytes attached to the signature

The complete verifier lives in `webhook.mjs`. The public value belongs only to this local example.

```js
import { createHmac, timingSafeEqual } from 'node:crypto';

export const fixtureSecret = 'local-writing-example';
export function sign(body) {
  return createHmac('sha256', fixtureSecret).update(body).digest('hex');
}
export function verify(body, signature) {
  if (typeof signature !== 'string' || !/^[a-f0-9]{64}$/.test(signature)) return false;
  return timingSafeEqual(Buffer.from(sign(body), 'hex'), Buffer.from(signature, 'hex'));
}
```

The format check ensures both buffers passed to `timingSafeEqual` have the same length. Node's [cryptography reference](https://nodejs.org/api/crypto.html#cryptotimingsafeequala-b) requires equal byte lengths and cautions that this function alone does not make surrounding code timing-safe.

The handler in `service.mjs` verifies the received buffers before parsing JSON, because parsing and reserializing can change the bytes. The altered-body check makes the consequence visible: a trailing space changes the signature even though the JSON value remains equivalent.

### Step 3: Inspect success and failure separately

The check sends a valid event, then changes its signature and body in separate requests. The recorded webhook output is:

```text
valid signature: 204
wrong, malformed, missing signatures: 401
body changed after signing: 401
signed invalid JSON: 400
```

The assertions require exactly one recorded event after those requests. An HTTP 204 by itself would establish only that the handler returned success.

If an invalid signature returns 204, stop: the example has not demonstrated rejection. If signed invalid JSON returns 204, the validation path disagrees with the stated event contract.

### Step 4: Start and stop the manual server

To inspect the service independently, run:

```bash
node service.mjs
```

Use the printed loopback URL in a second terminal. The port below is only an example:

```bash
export LAB_URL=http://127.0.0.1:49152
curl --fail-with-body "$LAB_URL/health"
```

Expect `{"status":"ok"}`. For connection refusal, correct the URL or start the server before sending another request.

Press Ctrl-C in the server terminal when finished. Restarting clears the server's in-memory state.

## Separate a teaching fixture from a production promise

Anyone can compute a signature using the fixture's public value, so the example demonstrates byte verification instead of protection from someone who knows that value. Hiding that boundary would make the tutorial look stronger and teach the reader less.

| Production question | What this fixture establishes | What remains unresolved |
| --- | --- | --- |
| Can a changed body pass the original signature? | The tested changed-body request returns HTTP 401 | A complete security review |
| Can a valid event be replayed? | Repeated valid requests are accepted | Timestamp policy and duplicate handling |
| Is an accepted event durable? | It is appended to an in-memory array | Storage and crash recovery |
| Does the code follow a vendor protocol? | It follows the protocol defined here | The actual provider's headers and signing rules |

The [Node HTTP reference](https://nodejs.org/api/http.html) documents the request and response primitives used by the fixture. A vendor tutorial needs the provider's documented signing protocol and real integration checks before it can replace this local example.

## Review the rendered path before publishing

I keep the review focused on what the next instruction needs: run the archive from a new directory and compare the rendered code with the supplied files. Record the runtime and raw output with the revision so another reviewer can repeat the check.

| Review question | Evidence to retain | Release decision |
| --- | --- | --- |
| Is every imported module supplied or installed? | Clean-directory command output | Hold if dependency resolution fails |
| Can the reader start and stop the service? | The printed URL and health response | Repair the missing command or prerequisite |
| Does the failure case actually fail? | Response status and stored-state assertion | Hold if rejected input changes accepted state |
| Does the prose exceed the test? | A claim beside its assertion | Narrow the claim or add a relevant test |
| Can an intended reader finish without help? | Their actual task log | Do not infer usability from the author's successful run |

The [recorded checks](/static/examples/writing-lab/validation.txt) passed on Node.js 24.18.0 on 10 September 2026. No human usability study was conducted.

The [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) provides the wider release review; [developer onboarding documentation](/articles/developer-onboarding-docs-what-works-what-doesnt/) applies the same prerequisite discipline to a contributor's first task. For different document jobs, compare the [technical writing examples](/articles/technical-writing-examples/).
