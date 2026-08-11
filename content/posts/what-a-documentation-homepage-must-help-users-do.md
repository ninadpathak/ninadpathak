---
title: "What a Documentation Homepage Must Help Users Do"
date: 2026-08-11
updated: 2026-08-11
description: "Design a documentation homepage around first actions, returning tasks, recovery paths, and clear routes instead of an equal-weight card wall."
tags: ["documentation", "developer-experience", "information-architecture"]
takeaways:
  - "A documentation homepage is a routing interface, not a visual inventory."
  - "Give new users, returning implementers, people in recovery, and evaluators distinct next moves."
  - "Test route labels, destinations, and audience before treating cards as navigation."
status: published
slug: "what-a-documentation-homepage-must-help-users-do"
---

A documentation homepage has a narrow job: help someone choose a useful next move before they understand the whole product. I reviewed [Stripe](https://docs.stripe.com/), [GitLab](https://docs.gitlab.com/), [GitHub](https://docs.github.com/), [Chrome](https://developer.chrome.com/docs), and [Google Maps](https://developers.google.com/maps/documentation) documentation homepages while building the route audit below, and the layouts vary far more than the underlying behavior.

Each homepage gives a reader a route, not just a collection of things to browse. That distinction is what separates a documentation landing page from an equal-weight card wall.

## Give the documentation homepage four reader routes

A homepage should help a new user start, a returning user resume work, a blocked user recover, and an evaluator understand the product surface. These are jobs, not mandatory visual sections.

| Reader situation | Homepage promise | A useful destination |
| --- | --- | --- |
| New to the product | Complete the first supported result | Quickstart or first request |
| Returning to implementation | Find an exact object or workflow | API reference or task guide |
| Blocked by a failure | Recover without searching the whole library | Troubleshooting or error guide |
| Evaluating the product | See which capability route applies | Product overview or capability guide |

The five homepages I inspected make different design choices, but they all make at least one route obvious. Stripe leads toward getting started and a runnable example, while GitLab places frequent answers ahead of broader product areas.

GitHub groups its library by jobs such as collaborative coding and CI/CD. Google Maps pairs a first action with capability routes, which keeps product discovery from replacing task completion.

## Make the first action more prominent than exploration

A new reader often arrives with a simple question: can I make this work? Put the shortest supported path near the top, then let broader product exploration follow.

Chrome’s documentation homepage establishes what the library contains, then gives product areas clear entry links. The point is not to copy Chrome’s layout.

Make the first decision smaller than “choose from everything we have.”

A card wall fails when every destination carries the same visual weight, even though one route is the safe first step and another is a niche reference page. Cards are fine when they identify a reader, a job, and a destination.

## Make labels describe the route

A reader should be able to predict the next page from the label alone. `Send your first request` and `Troubleshoot failed requests` expose an outcome, while `Resources` and `Learn more` make the reader open a page to discover what it contains.

That rule applies to links, headings, and navigation labels. Use the same language across them where possible, then review the outline with the method in [How to Write Task-Based Documentation Headings](/articles/how-to-write-task-based-documentation-headings/).

## Test the homepage as a route inventory

I built a small [documentation homepage route audit](/static/downloads/documentation-homepage-audit/README.md) to turn this into a check instead of a design opinion. The fixture requires four route jobs, unique labels, a destination, and a named audience.

```bash
python3 audit_homepage_routes.py example-homepage-routes.json
```

```text
PASS
4 routes cover: exploration, first action, recovery, returning task
```

The script cannot prove that a reader will understand your labels. It can catch a more basic failure before the homepage ships: a route inventory that has forgotten the person who needs help after the happy path breaks.

## Keep homepage scope separate from site organization

A homepage should route readers into the documentation system. It should not carry the full burden of URL migration, sidebar design, canonical ownership, or every product page.

For that wider work, use [How to Organize Documentation That Has Drifted](/articles/how-to-organize-a-documentation-site/). Start the homepage audit with the page’s likely entry tasks, then make each chosen route lead to a page that actually completes its promise.

A good documentation homepage makes the next decision easier. If a reader still has to infer where to begin, which page owns their task, or where to recover from failure, the homepage is still acting like a card wall.
