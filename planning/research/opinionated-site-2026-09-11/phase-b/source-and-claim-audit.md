# Phase B source and claim audit

Audit date: 2026-09-11. Scope is limited to the four Phase B articles. This record supports independent review; it does not certify the rest of the archive.

## Dispositions

| Article | Thesis | Fair default or opposing view | Claim disposition |
| --- | --- | --- | --- |
| `developer-onboarding-docs-what-works-what-doesnt.md` | Onboarding documentation should end in a safe merged change, not a completed reading list. | Teams front-load architecture because they want understanding before contribution; the rewrite argues that one working request gives the architecture a hook. | `PROVISIONAL_REVIEW`: no automated provenance candidate; fictional Orbit example labeled; independent review accepted Phase B. |
| `documentation-review-checklist-before-you-publish.md` | Documentation review should verify product truth before polishing prose. | Copyediting matters, but it cannot establish product behavior and can make a false instruction look trustworthy. | `PROVISIONAL_REVIEW`: no automated provenance candidate; fictional Orbit contract labeled; independent review accepted Phase B. |
| `documentation-style-guide-template-for-developer-teams.md` | A product style guide should record decisions and sources rather than collect taste. | Broad voice and language guides remain useful, but they cannot define a local product term, tested command, or released UI state. | `PROVISIONAL_REVIEW`: the unsupported authorship claim was removed; the linked template is presented without attributing its creation; no automated provenance candidate remains; independent review accepted Phase B. |
| `how-to-organize-a-documentation-site.md` | Documentation navigation should follow reader routes rather than the org chart. | A platform redesign can improve presentation, but it cannot settle duplicate answers, canonical ownership, or reader intent by itself. | `PROVISIONAL_REVIEW`: no automated provenance candidate; fictional Orbit example labeled; independent review accepted Phase B. |

## Primary-source checks

The following public sources returned HTTP 200 on 2026-09-11 and were inspected for the claims carried into the articles.

| Source | Claim supported |
| --- | --- |
| [Microsoft Engineering Fundamentals onboarding template](https://microsoft.github.io/code-with-engineering-playbook/developer-experience/onboarding-guide-template/) | Separates goals, contacts, team agreements, setup, project building blocks, and resources; permits the guide to link to existing project material. |
| [Microsoft project and repository guidance](https://microsoft.github.io/code-with-engineering-playbook/documentation/guidance/project-and-repositories/) | Treats project setup, build, test, deployment, and working agreements as repository documentation concerns. |
| [Corepack maintained README](https://github.com/nodejs/corepack/blob/main/README.md) | Defines `packageManager` as a manager-and-version selection, documents the supported manager names, and describes `corepack enable [name]` plus `corepack install`. This supports checking the selected manager's version instead of mistaking `corepack --version` for that check. |
| [GitLab onboarding handbook](https://handbook.gitlab.com/handbook/people-group/general-onboarding/) | Uses onboarding issue tasks with ownership, due dates, and department or role-specific work. |
| [GitLab documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) | Encourages documentation in the code merge request or a nearby merge request and separates technical-writer, code-reviewer, and maintainer responsibilities. |
| [GitLab documentation review apps](https://docs.gitlab.com/development/documentation/review_apps/) | Builds and deploys a documentation preview from a merge request. |
| [Google heading guidance](https://developers.google.com/style/headings) | Recommends descriptive headings, logical heading levels, and content between a parent heading and its subsections. |
| [Google word list](https://developers.google.com/style/word-list) | Records preferred wording and usage decisions for Google's own documentation. |
| [Google UI guidance](https://developers.google.com/style/ui-elements) | Gives conventions for naming menu paths and visible controls. |
| [Google command-line syntax guidance](https://developers.google.com/style/code-syntax) | Introduces commands by task and separates procedural options. |
| [W3C page-structure tutorial](https://www.w3.org/WAI/tutorials/page-structure/) | Covers page regions, region labels, headings, and content structure. |
| [Diataxis](https://diataxis.fr/start-here/) | Distinguishes tutorials, how-to guides, reference, and explanation by reader need. |
| [GitLab documentation folder structure](https://docs.gitlab.com/development/documentation/site_architecture/folder_structure/) | Declares separate path boundaries for user, administration, API, development, installation, update, and tutorial documentation. |
| [GitLab documentation style guide](https://docs.gitlab.com/development/documentation/styleguide/) | Provides a maintained public editorial convention set. |
| [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) | Provides a maintained public voice and terminology reference. |
| [AWS Lambda developer guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) | Public render exposes global navigation, guide navigation, breadcrumbs, and a current-page outline as distinct layers. |

## Removed or bounded claims

- Removed the unsupported statement that an earlier version of this site forced a first-person counter.
- Removed unproven onboarding productivity and time claims. The page now asks teams to record route failures and undocumented decisions without publishing a universal benchmark.
- Labeled illustrative services, hosts, commands, recovery snippets, paths, roles, responses, and migration decisions before the reader encounters them. This includes the reserved `example.com` domain and the fictional Orbit host.
- Kept no anonymous quote, client incident, private role, internal result, or claimed personal product use.
- Removed the style-template authorship claim. Artifact existence does not prove who created it.
- Replaced `corepack --version` with a `pnpm --version` check tied to the illustrative `"packageManager": "pnpm@10.17.1"` field. The recovery branch uses Corepack commands documented by its maintained primary source.

## Editorial pattern correction

The second Phase B pass removed the repeated "passes when / fails when" verdict rhythm across the four bodies. Failure branches remain where they direct a repair, stop, redirect, recovery, or evidence decision. Redundant H3s and repeated checklist or FAQ material were removed. The organization heading now promises a content route, matching its Guides, API reference, SDKs, Release notes, and Support examples.

## Second-review visual correction

The public style-guide sentence now ends after "The downloadable template records those decisions." Attribution review stays in this evidence file rather than leaking into public prose.

The shared image reset now declares `height: auto`. A direct static image makes its `.visual-container` content-sized, while iframe containers retain their fixed desktop and mobile heights. Browser checks compare each affected image's rendered ratio with its natural ratio, assert that the image bounding box fits its container, and separately protect a responsive flowchart and iframe visual from regression.

## URL and title decisions

No slug, canonical, or redirect changed. Titles changed in place:

| Stable slug | New title |
| --- | --- |
| `developer-onboarding-docs-what-works-what-doesnt` | Developer Onboarding Docs Should End in a Merged Change |
| `documentation-review-checklist-before-you-publish` | Documentation Review Should Start With the Product, Not the Prose |
| `documentation-style-guide-template` | A Documentation Style Guide Should Record Decisions, Not Taste |
| `how-to-organize-a-documentation-site` | Organize Documentation Around Reader Routes, Not Your Org Chart |
