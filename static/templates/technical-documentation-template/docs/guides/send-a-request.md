# Send a request

Use a complete request and an observable response before you introduce optional parameters.

## Request

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer REPLACE_WITH_TEST_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"message":"hello"}' \
  https://api.example.test/v1/messages
```

## Expected result

Document the response fields that let a reader confirm the request succeeded. Put field meanings in the [configuration reference](../reference/configuration.md) when they need more detail.
