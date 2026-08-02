# Troubleshooting

Keep this page limited to failures the product team can recognize and reproduce.

## `401 Unauthorized`

Check that the token belongs to the environment in the request URL and that the account has the required scope. Create a fresh test token before retrying.

## `404 Not Found`

Check the API version and resource path. A working request from [Send a request](guides/send-a-request.md) is the baseline before you add optional path segments.
