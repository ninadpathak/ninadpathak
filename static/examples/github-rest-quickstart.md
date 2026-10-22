# Get a repository's details from the GitHub REST API

<!-- Filled example of quickstart-template.md. No token needed. -->

At the end you will have a repository's full name, default branch and license, read from the GitHub REST API with `curl`.

## Before you start

You need:

- curl 7.76.0 or later, for `--fail-with-body`. Check with `curl --version`; if it is older, install a current curl from your package manager or https://curl.se/download.html.
- jq, to pull fields out of the JSON. Check with `jq --version`.

No GitHub account or token is needed: unauthenticated requests get 60 requests per hour per IP address.

```bash
curl --version | head -1
jq --version
```

## Step 1: Request the repository

```bash
curl -sS --fail-with-body \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/kubernetes/kubernetes \
  -o repo.json
```

## Step 2: Read the fields you need

```bash
jq -r '.full_name, .default_branch, .license.spdx_id' repo.json
```

## See it work

You should see:

```text
kubernetes/kubernetes
master
Apache-2.0
```

## If it fails

| What you see | Why | Fix |
|---|---|---|
| `curl: (22) The requested URL returned error: 404` and `"message": "Not Found"` | The owner or repository name is misspelled, or the repository is private | Check the URL path; private repositories need a token |
| A `403` or `429` status, and `x-ratelimit-remaining: 0` in the headers | The 60 unauthenticated requests for this hour are used up | Wait until the time in `x-ratelimit-reset`, or send a token |
| `jq: command not found` | jq is not installed | Install jq, or open `repo.json` and read the fields directly |

## Next steps

- Check how many requests you have left: `curl -sS -I https://api.github.com/rate_limit | grep -i x-ratelimit-remaining`.
- Read the [repository endpoint reference](https://docs.github.com/en/rest/repos/repos#get-a-repository) for every field in `repo.json`.
