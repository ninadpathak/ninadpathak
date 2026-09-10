# Writing lab

This synthetic local service supports examples about technical documentation. It accepts export records and signed webhook events. It has no external account, real customer data, or file-export worker.

Use Node.js 24.18.0, the recorded test version. The project has no npm dependencies. Extract the archive into a new directory, open `writing-lab`, then run:

```bash
node --version
node check.mjs
```

A successful run ends with `PASS`. Any assertion failure means the stated behavior has not been reproduced; keep the output and investigate before using the article's conclusions. The check creates isolated servers on loopback ports, then closes them.

For a manual request, follow [getting started](docs/getting-started.md). Run `node service.mjs`; use the printed URL in another terminal. Stop the server with Ctrl-C when finished.

## Fixture boundaries

The webhook signature is a synthetic HMAC-SHA256 protocol over exact request bytes. `local-writing-example` is a public test value, not a credential. No signature timestamp or replay prevention is implemented. Repeating a valid event records it again. This is not a provider SDK or a production webhook handler.

The export route keeps a map in one server instance. Matching keys and formats return the existing record. Conflicting formats return HTTP 409. Stopping the server erases its records. There is no authentication, persistence, or export generation. Do not deploy this fixture.

## Reproducing the earlier missing import

From a new directory, run:

```bash
node --input-type=module -e 'import { verifyWebhook } from "@example/webhooks"'
```

The recorded clean-directory run failed with `ERR_MODULE_NOT_FOUND`. This demonstrates that the earlier article did not supply a runnable dependency path. It does not establish whether a similarly named package exists in a registry.

## Inspecting the documented changes

- [Quickstart](docs/getting-started.md): start the service and store a first request.
- [Request guide](docs/send-a-request.md): recover from a deliberately dropped response.
- [Reference](docs/reference.md): check input and retention rules.
- [Troubleshooting](docs/troubleshooting.md): choose an action from the observed failure.

The checks were run by the publishing agent. No human usability test or production incident is claimed.
