# Recover an accepted request whose response was lost

Keep the server from the quickstart running. Retain its printed URL in `LAB_URL`. Use a new key, `report-loss`, for this experiment; repeating the experiment with that key returns its previous record instead of dropping the response again.

```bash
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-loss' \
  -H 'X-Fixture-Drop-Response: yes' \
  --data '{"format":"csv"}'
```

Expect curl to exit with code 52, `Empty reply from server`. The fixture stores the record, then closes the connection before sending a response. This deliberately lost response represents an ambiguous client outcome; it is not a measured network timeout. If you receive HTTP 200, the key was already used. Choose another unused key to repeat the experiment.

Repeat the request with the same key and format, omitting the fixture failure header:

```bash
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-loss' \
  --data '{"format":"csv"}'
```

Expect HTTP 200 with the stored identifier. A different key would create a separate record. HTTP 202 on this retry means the current server had no retained entry: the key changed or the server was replaced. Investigate before treating it as the original operation. See [the retention boundary](reference.md) and [the recovery table](troubleshooting.md).
