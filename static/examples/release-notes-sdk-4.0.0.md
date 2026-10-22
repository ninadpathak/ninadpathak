# Example SDK 4.0.0 release notes

<!-- Filled example of release-notes-template.md for a hypothetical SDK. -->
Version: 4.0.0
Date: 2026-07-30
Compatibility: Breaking changes to pagination and Node.js support
Affected: JavaScript SDK users and REST integrations that send `page`. Python SDK users can ignore this release.
Action: Upgrade to Node.js 20, then migrate list calls from `page` to cursors
Rollback: Safe until the application stores its first v4 cursor; after that, contact support before downgrading

## Breaking changes

### List endpoints use cursors instead of page numbers

What changed: `list()` no longer accepts `page`. It returns `nextCursor`, which you pass back as `cursor`.
Migration: Replace `page: n` with the `cursor` returned by the previous call, starting from no cursor.
Verify: A full pagination run returns every record exactly once, and the last page returns `nextCursor: null`.
Deadline: 2026-09-30

### Node.js 18 is no longer supported

What changed: The SDK now requires Node.js 20 or later.
Migration: Upgrade development, CI and production runtimes before installing 4.0.0.
Verify: `node --version` prints v20 or later in every environment that runs the SDK.
Deadline: None

## Security and support

- Version 3 security support ends 2026-09-30.
- Runtime requirement: Node.js 20 or later.

## Fixes

- Webhook retries no longer resend an event after a `2xx` response: integrations that saw duplicate deliveries.

## New capabilities

- `client.orders.list({ cursor, limit })`: see the pagination guide.

## Known issues

### Filtered list with zero results returns an empty string for nextCursor

Workaround: Treat both `""` and `null` as the end of the list.
Tracking: SDK-917
Fixed in: 4.0.1

## Resources

- Migration guide: /docs/migrate-to-v4
- Reference changes: /docs/reference/orders#list
- Support: /support
