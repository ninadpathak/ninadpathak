# Get started

This page owns the first successful request. Keep prerequisites, setup, expected output, and the next task together.

## Prerequisites

- A test account with permission to create a token
- Python 3.11 or later
- A safe place to store the token outside source control

## Verify access

Replace the placeholder URL and token with values from your product before publishing this command.

```bash
curl --fail-with-body \
  --header "Authorization: Bearer REPLACE_WITH_TEST_TOKEN" \
  https://api.example.test/v1/health
```

A useful guide shows the successful response and links to [troubleshooting](troubleshooting.md) when the request fails.
