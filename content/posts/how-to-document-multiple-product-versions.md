---
category: technical-documentation
date: 2026-08-12
description: Document supported, retired, and historical product versions with stable
  URLs, version labels, canonicals, redirects, and tested route policies.
slug: how-to-document-multiple-product-versions
status: published
tags:
- documentation
- developer-experience
- documentation-seo
takeaways:
- A version label is a support promise, not a navigation decoration.
- Supported versions need distinct, self-canonical URLs when their instructions differ.
- Redirect retired instructions only when the target can still complete the same reader
  task.
title: How to Document Multiple Product Versions
updated: 2026-08-12
---

A version switcher can make incompatible instructions look like interchangeable pages. I built a [version-route audit download](/static/downloads/documentation-version-route-audit/docs-version-route-audit.py) because a current page, a supported older page, and a retired page need different URL behavior before a canonical tag or redirect can be correct.

The policy is simple: keep instructions reachable and self-canonical while the product version remains supported. Redirect a retired task only when the destination still gives the reader a valid path, and preserve a historical version when its instructions remain useful evidence rather than a trap.

## Product documentation versioning checklist

Use this table to establish the policy before configuring navigation or search metadata. It separates a version that a developer can still use from one that only needs a record of where the old URL went.

| Version state | URL behavior | Canonical | Reader-facing label |
| --- | --- | --- | --- |
| Current supported version | Stable, direct URL | Self-canonical | Current |
| Older supported version | Stable, direct URL | Self-canonical | Supported version |
| Retired version with an equivalent replacement | Permanent redirect to the replacement | No page to canonicalize after redirect | Retired and redirected |
| Historical version with distinct instructions | Stable, direct URL | Self-canonical | Historical or unsupported |

A canonical consolidates duplicate or very similar pages. It is not a safe way to merge materially different setup steps, API fields, authentication rules, or migration boundaries.

## Audit documentation versions before choosing redirects

Start by treating each version as a reader task. A path is distinct when following one version's instructions against another version can fail, change data, or produce an unsupported integration.

Google's [canonicalization guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) frames canonicalization as a preference among duplicate or very similar URLs. That boundary matters in product documentation because versioned pages often look similar in a template but carry different behavior.

### Define which versions are supported

Publish a small support matrix close to the version switcher and on the page itself. State the version, support state, relevant release date, and the route to migration guidance when the page is no longer current.

The word `latest` is not enough. It becomes misleading as soon as a developer lands on a bookmarked versioned URL or copies a command into a long-running service.

### Keep supported versions on distinct self-canonical URLs

A supported version needs a stable URL, a visible label, and its own self-referencing canonical. That gives the developer a link they can share and stops the current version from silently claiming ownership of instructions that are still valid elsewhere.

[Docusaurus versioning](https://docusaurus.io/docs/versioning) preserves a copy of documentation when a new version is created, which is the useful model here. The preserved set remains inspectable as the current documentation continues to change.

### Redirect only when the replacement preserves the task

A permanent redirect is a strong signal that the target replaces the original URL. Google's [redirect documentation](https://developers.google.com/search/docs/crawling-indexing/301-redirects) describes redirects as a canonicalization signal, so send a retired documentation URL to a target that can actually replace its reader outcome.

Redirecting `/docs/v1/authentication/` to a general release note fails that test. Redirect it to the equivalent current authentication guide only when the current guide includes the migration boundary, or keep a historical page that says why the old path no longer works.

## Test the version route inventory

A version policy turns into a release gate when the routes are stored as data. I ran the script against a fixture that rejects a supported page with another version's canonical and a retired page without an inventory target, then reran it after repairing the route policy.

```bash
python3 docs-version-route-audit.py version-routes-pass.json
```

The expected result is a `PASS` line naming the route count. The script checks route policy, not whether an SDK call still succeeds, so pair it with runnable examples and a release review.

<div class="visual-wrapper">
  <div class="visual-title">Version route audit on a repaired documentation fixture</div>
  <div class="visual-container" style="height: auto; aspect-ratio: 2560 / 1664; background: #0d0f14; overflow: hidden;">
    <img src="/static/images/articles/how-to-document-multiple-product-versions/version-route-audit.png" alt="MacBook Air terminal window showing a passing version route audit for three documentation routes" loading="lazy" style="display: block; width: 100%; height: 100%; object-fit: contain;">
  </div>
</div>
<p class="visual-caption">The receipt confirms that current, supported, and retired routes follow the declared policy.</p>

## Link readers to the right documentation version

A version switcher should change the page, not only the label. Keep version choices in ordinary crawlable links, then make the active version visible near code blocks, prerequisites, and migration notices.

The [documentation homepage guide](/articles/what-a-documentation-homepage-must-help-users-do/) explains why a route label needs to predict the page that follows. Apply the same standard here: `v2 supported documentation` is useful, while `Other versions` makes a developer open another interface before learning whether their task is covered.

The [documentation SEO guide](/articles/seo-for-technical-documentation/) shows how to audit the canonical, title, links, image text, and sitemap after the route policy is settled. Version policy comes first because search metadata cannot repair a path that sends a developer to the wrong instructions.

## Preserve historical pages that still explain a real state

An unsupported page can still earn a stable URL when it documents a deployment a reader must maintain, a security boundary, or a migration that cannot be reversed. Mark its support state plainly and link to the current version without pretending both pages say the same thing.

The competent objection is that keeping old pages adds maintenance and duplicate-content risk. That is true when old pages are vague copies, but deleting or canonicalizing a page with different working instructions sends developers to an answer that may be wrong for their installed version.

A versioned documentation system works when the URL, page label, canonical, redirect behavior, and migration path tell the same story. Start with the routes developers already bookmark, then test the policy whenever a release changes which instructions remain safe to follow.
