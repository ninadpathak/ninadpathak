# First technical-writing refresh batch

Prepared 10 September 2026 by the sole publishing owner, after root acceptance of deployed commit `d83ac73f039dc14f9824f00287c719f29bf8be88`. This batch is local and uncommitted. No article changes were pushed or deployed.

## Owned surfaces

- `content/posts/how-to-write-a-technical-tutorial-that-actually-teaches.md`: complete tutorial method with a supplied webhook fixture, genuine missing-import receipt, success and failure checks, and production boundaries.
- `content/posts/technical-documentation-template.md`: retained blank starter plus filled product documentation, distinct page responsibilities, recovery and maintenance checks.
- `content/posts/technical-writing-examples.md`: eight writing formats with original annotations and concrete reader tasks, plus a portfolio annotation. This is a range-of-formats article, not another retry tutorial.
- `static/examples/writing-lab/` and `static/examples/writing-lab.zip`: shared synthetic fixture, complete Markdown pages, runtime version and public validation record.
- This evidence directory: reproducible commands, receipts, correction evidence and rendered screenshots.

The three canonical slugs and published status are retained. Updated dates are 10 September 2026. Their new contents require review before publication.

## Reproduce the fixture

From the repository root:

```bash
unzip static/examples/writing-lab.zip -d /tmp/writing-lab-review
cd /tmp/writing-lab-review/writing-lab
node --version
node check.mjs
```

Use a new extraction directory if that path already belongs to another task. The recorded runtime is Node.js 24.18.0 on macOS arm64. No npm dependencies are needed. A passing run ends with `PASS`; a failing assertion blocks the associated article claim.

The test starts loopback servers on operating-system-assigned ports and closes them. It covers valid signatures, wrong/malformed/missing signatures, altered raw bytes, signed invalid JSON, an intentionally lost response after storage, matching-key recovery, conflicting formats, a new-key duplicate, invalid input, a partial-upload disconnect, 4096/4097-byte boundaries, valid-event replay, and a fresh instance's empty state.

The rejected-event state assertion remains before the replay check: one valid event is retained after invalid cases, then a separate valid replay increases the count to two. The partial-upload test waits for the server's request and aborted events; it does not depend on a fixed sleep.

To recreate the evidence, run `python3 planning/research/writing-refresh-2026-09-10/reproduce.py` from the repository root. This refreshes this batch's owned evidence and archive; it does not publish anything. It also runs curl against a temporary server and terminates that server afterward.

## Actual failed attempts and corrections

`missing-import.log` records the old article's import in a fresh directory. The result is `ERR_MODULE_NOT_FOUND`. It demonstrates missing setup in the article, not registry nonexistence.

An independent fixture reviewer found that disconnecting during request upload escaped the original async iterator as `ECONNRESET`, terminating the server. `before-service.mjs` preserves that implementation, and `aborted-upload-before.log` reproduces its nonzero exit with the current regression check. The corrected handler catches request-read failure and destroys the incomplete response without processing or storing the body. Root relayed independent confirmation that the server remains alive with prior state intact.

The same reviewer requested adjacent body-limit tests and an explicit replay test. Both are now in `check.mjs` and in the final archive's receipt. The fixture intentionally lacks replay prevention; the article states that limit.

The initial paragraph-formatting pass damaged the final Markdown delimiter in each article. Those three delimiters were repaired manually. Render checks count every table and its final body rows, reject stray pipe paragraphs, and check desktop/mobile overflow. No further generic prose formatting is applied to table syntax.

The template initially placed cleanup before recovery. Cleanup now follows recovery so the reader keeps the same instance and URL throughout.

## Provenance and scope

The publishing agent authored and executed the synthetic tests. No test is attributed to Ninad's personal work, a customer incident or a real export vendor. The articles use neutral dated validation notes and link to the public fixture receipt.

Root relayed an independent AI review using only the filled documentation. Its decisions matched all three recovery cases: reuse the saved key/format on the same instance after a lost response, restore the original format after HTTP 409, and stop recovery after restart. This is an AI reviewer inspection, not a human trial or a usability measurement. No human completion time or improvement is claimed.

The fixture accepts records but does not generate files. State is held in one process instance; no restart durability, multi-instance guarantee or production security property is claimed. The webhook key is an explicitly public synthetic value. There is no replay protection, vendor signing protocol or external service account.

Primary source verification on 10 September 2026:

- Node.js cryptography reference: https://nodejs.org/api/crypto.html#cryptotimingsafeequala-b — equal byte lengths and the limits of timing-safe comparison.
- Node.js HTTP reference: https://nodejs.org/api/http.html — the request/response primitives used by the local fixture.

`voice-check.json` compares first-person counts with the deployed baseline. The examples refresh removes unrelated personal work and result claims rather than inventing replacement experience. First-person editorial judgments remain; all fresh empirical statements are attributed to test artifacts.

## Validation and cleanup

- `clean-check.log`, `archive-check.log`: final fixture passes from fresh directories.
- `manual-curl.json`: health, first acceptance, deliberate connection loss (curl 52), and retained-record recovery (HTTP 200).
- `starter-build.log`: existing blank archive extracted into a fresh Python environment; navigation/link validator and strict MkDocs build pass.
- `quality.log`: site build, 666 tests with four skips, and strict cluster/stylesheet/structure/inert-CSS gates.
- `editorial-check.log`: zero rule-checker errors; residual semicolon warnings and informational no-visual notices are retained, not hidden.
- `claims-check.log`: zero automatically detected claim candidates. The separate claim ledger supplies manual scope classification.
- `render-checks.json` and PNGs: full pages and final tables at desktop/mobile sizes.
- `preservation.json`: eight prior dirty files unchanged and unstaged; three canonical URLs retained.

The build produces 87 articles, 141 HTML pages and 140 unique canonical/sitemap URLs. No existing asset or blank starter was replaced. Temporary fixture servers and visual preview processes are stopped. No recurring work or monitoring was created. Full-quality runs need no repetition unless the reviewer changes source or identifies a new concern.
