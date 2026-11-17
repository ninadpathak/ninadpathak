---
category: technical-documentation
primary_query: how to write a technical tutorial
siblings:
- documentation-types
- documentation-review
- developer-onboarding-docs
date: 2026-04-02
description: How to write a technical tutorial that one reader can finish. Pick a starting
  state and a result they can check, build the path before the prose, and test every step
  from a clean directory.
slug: writing-technical-tutorials
status: published
work_note: "I build every tutorial before I write it up, so your engineers review working code. This post is my method for a tutorial a reader can finish. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Work with me on your tutorials](/services/)."
takeaways:
- Choose one reader, one starting state and one result the reader can check.
- Build and run the working path before you write the explanation around it.
- Give every step a checkpoint, with the output the reader should see.
- Run every step from a clean directory before you publish.
title: How to Write a Technical Tutorial a Reader Can Finish
updated: 2026-09-10
---

A famous first lesson in programming is a C program that prints "hello, world". It comes from a 1974 Bell Labs memo by Brian Kernighan that was itself titled [Programming in C: A Tutorial](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program), and it works because the reader can see on the screen whether they got it right.

To write a technical tutorial, pick one reader and one starting state, build a path to a result that reader can check, and run every step from a clean directory before you publish. I don't call a page a tutorial because it has numbered steps and code blocks.

An earlier version of this page failed that test. Its example imported `verifyWebhook` from a package named `@example/webhooks` without telling the reader how to install it, so the first command failed in an empty directory.

The example below replaces it, as part of my pages on [technical documentation](/articles/technical-documentation/). It's a small webhook receiver with no dependencies, and every command and output on this page comes from running it.

## What makes a page a technical tutorial?

A technical tutorial takes one reader from a stated starting point to a result they can see. A reference page answers a lookup, such as the format of a signature header, and a tutorial has the reader build something.

If your reader only needs the definition of a signature field, give them a reference page. The [documentation types guide](/articles/documentation-types/) covers which page type fits which need.

## How do you define the reader and the result?

Write down the starting state before you write a step. For the webhook example, the reader can run JavaScript from a terminal, and these are the things I check before they start:

| Requirement | Check | If it fails |
| --- | --- | --- |
| Node.js 24.18.0, the recorded test version | `node --version` | Use the recorded version before comparing results |
| An extracted copy of the fixture | Confirm `service.mjs`, `webhook.mjs`, and `check.mjs` exist | Extract the complete archive |
| A successful event and a rejected signature | Run `node check.mjs` | Inspect the failing assertion before describing the example as runnable |

The result is small on purpose. The reader's receiver accepts an event signed with the fixture's test secret, rejects an event whose bytes were changed, and records only the accepted event.

I'd never call that a production webhook system in the tutorial. A tutorial that claims more than its example shows is teaching the reader something false.

## How do you build a tutorial around checkpoints?

Give every step a command and the output the reader should see after running it. The fixture uses Node's built-in HTTP and crypto modules to compute an HMAC-SHA256 digest over the exact bytes of the request, so nothing has to be installed.

### Step 1: Create the project from the complete fixture

[Download the writing lab](/static/examples/writing-lab.zip), extract it into an empty directory, and open the `writing-lab` folder in a terminal. The archive holds the receiver and its checks, and it has no npm dependencies.

```bash
node --version
node check.mjs
```

I reran those two commands on November 18, 2026 with Node.js 24.22.3. The check printed `PASS` and closed the servers it had started.

If Node reports that a file can't be imported, compare your extracted folder with the archive before you install anything. You can reproduce the old page's failure in an empty directory with this command:

```bash
node --input-type=module -e 'import { verifyWebhook } from "@example/webhooks"'
```

Node answers with `ERR_MODULE_NOT_FOUND`, because the instructions never supplied that package. Swapping in another unexplained import would have left the same hole in the tutorial.

### Step 2: Keep the bytes attached to the signature

The whole verifier is in `webhook.mjs`. The secret in it is public and belongs only to this local example.

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

The format check on the signature makes sure both buffers passed to `timingSafeEqual` are the same length. Node's [crypto reference](https://nodejs.org/api/crypto.html#cryptotimingsafeequala-b) says the function throws an error when the two byte lengths differ.

The handler in `service.mjs` verifies the received bytes before it parses them as JSON. Parsing and re-serializing can change the bytes, and the check shows the effect: adding one trailing space to the body makes the signature fail, even though the JSON value is the same.

### Step 3: Inspect success and failure separately

The check sends one valid event, then sends requests with a wrong signature and with a changed body. The first lines of its output are:

```text
valid signature: 204
wrong, malformed, missing signatures: 401
body changed after signing: 401
signed invalid JSON: 400
```

The check also asserts that exactly one event was recorded after those requests. A 204 alone would show that the handler returned success, and it wouldn't show that the bad requests were kept out.

If a request with an invalid signature returns 204, stop there, because the example hasn't shown rejection. If signed but invalid JSON returns 204, the handler isn't validating the event the way the tutorial says it does.

### Step 4: Start and stop the manual server

To try the receiver by hand, start it:

```bash
node service.mjs
```

The server prints a loopback URL. Use that URL in a second terminal, in place of the example port below:

```bash
export LAB_URL=http://127.0.0.1:49152
curl --fail-with-body "$LAB_URL/health"
```

The health endpoint answers `{"status":"ok"}`. If curl reports a refused connection, the URL is wrong or the server isn't running.

Press Ctrl-C in the server's terminal when you're done. The receiver keeps its events in memory, so a restart clears them.

## What should a tutorial say about its limits?

A tutorial should say what its example doesn't prove, in the tutorial itself. Anyone can compute a valid signature with this fixture's public secret, so the example shows byte verification and offers no protection against someone who knows the secret.

| Production question | What this fixture establishes | What remains unresolved |
| --- | --- | --- |
| Can a changed body pass the original signature? | The tested changed-body request returns HTTP 401 | A complete security review |
| Can a valid event be replayed? | Repeated valid requests are accepted | Timestamp policy and duplicate handling |
| Is an accepted event durable? | It is appended to an in-memory array | Storage and crash recovery |
| Does the code follow a vendor protocol? | It follows the protocol defined here | The actual provider's headers and signing rules |

The [Node HTTP reference](https://nodejs.org/api/http.html) documents the request and response objects the fixture uses. A tutorial for a real provider, such as Stripe or GitHub, has to follow that provider's documented signing rules and test against the provider's own events.

## How do you review a tutorial before publishing?

Review a tutorial by running the archive from a new directory and comparing the code on the page with the files in the archive. I save the Node version and the raw output with the revision, so the next reviewer can repeat the run.

| Review question | Evidence to retain | Release decision |
| --- | --- | --- |
| Is every imported module supplied or installed? | Clean-directory command output | Hold if dependency resolution fails |
| Can the reader start and stop the service? | The printed URL and health response | Repair the missing command or prerequisite |
| Does the failure case actually fail? | Response status and stored-state assertion | Hold if rejected input changes accepted state |
| Does the prose exceed the test? | A claim beside its assertion | Narrow the claim or add a relevant test |
| Can an intended reader finish without help? | Their actual task log | Do not infer usability from the author's successful run |

The [recorded checks](/static/examples/writing-lab/validation.txt) are from September 10, 2026 on Node.js 24.18.0, and my rerun on Node.js 24.22.3 printed the same lines. I haven't tested the tutorial with outside readers, so the last row of that table is still open for this page.

For the release review that covers the rest of a docs page, see the [documentation review checklist](/articles/documentation-review/). [Developer onboarding documentation](/articles/developer-onboarding-docs/) applies the same starting-state check to a new contributor's first task.

Writing tutorials this way for a product is work I take on, described under [technical tutorials](/services/technical-tutorials/).

## FAQ

**How long should a technical tutorial be?**

Long enough to reach one result the reader can check, and no longer. The webhook example here has four steps, and each step ends with output to compare.

**What is the difference between a tutorial and a how-to guide?**

A tutorial teaches by having the reader build a small working thing from a known start. A how-to guide helps a reader who already knows the product finish one task in their own project.

**Should a tutorial include error cases?**

Yes, for the failures a reader is likely to hit on the path. The page above shows the missing-import error and the rejected signature, with the output each one produces.

**How do you test a technical tutorial?**

Run every command in order from an empty directory on the runtime version you name, and keep the output. Then ask someone from the intended audience to do the same and keep their log.
