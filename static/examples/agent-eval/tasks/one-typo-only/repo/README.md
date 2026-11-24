# notifier

Sends a webhook when a build finishes.

## Setup

Set `NOTIFIER_URL` to the endpoint that should recieve the webhook. The request is a POST with a JSON body.

## Retries

If an error occured while sending, the notifier trys again after 5 seconds, up to 3 times.

## Licence

MIT
