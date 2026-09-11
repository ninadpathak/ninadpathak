---
category: technical-documentation
date: 2026-04-01
description: Build developer onboarding docs around one supported setup path and a safe first merged change, with proof and recovery at each fragile step.
slug: developer-onboarding-docs-what-works-what-doesnt
status: published
work_note: "From access requests to a verified change, [Ninad Pathak](/contact/) writes technical onboarding documentation that gives a new engineer a route through setup and review rather than another reading list."
tags:
- technical-writing
- developer-experience
- documentation
takeaways:
- Make a safe first merged change the finish line instead of assigning a reading list.
- Give the reader one supported setup path with proof after each stage.
- Put help and recovery beside the command that can fail.
- Review the route when the product or development workflow changes.
title: Developer Onboarding Docs Should End in a Merged Change
updated: 2026-09-11
---

Picture a hypothetical day two: a new engineer is asking which Node version to use, whether Docker is required, and where the test credentials live. The answers exist.

One sits in the README, another survived in Slack, and the setup script quietly assumes the third.

A teammate can walk them through it, so the machine eventually runs. That rescue feels helpful while the onboarding guide keeps lying.

It says the route is documented when the route still lives in somebody's head.

Developer onboarding docs should end in a safe merged change, not a finished reading list. My rule is blunt: if the guide cannot carry someone from a clean machine through setup, review, and proof in a test environment, it is company background with a checklist attached.

## Design the route backward from the first merge

"Learn the codebase" has no visible finish line. Replace it with a contained result: run the product, change one user-facing behavior, pass the required checks, open a pull request, and verify the merged result.

The default approach front-loads architecture because the team wants the new engineer to understand the system before touching it. The intention is fair.

The sequence is backwards. A request flow makes more sense after the reader has sent one request through it.

### Declare the result before the setup begins

Put a completion contract near the top of the page. A reviewer should be able to test each line without interpreting "familiar" or "comfortable."

The illustrative contract below names no real product or team:

```text
Onboarding route complete when:
[ ] The API and database run locally.
[ ] GET /health returns 200 and the current commit SHA.
[ ] The starter test fails before the change and passes after it.
[ ] CI passes on the pull request.
[ ] The change appears in the test environment.
```

Replace any line that asks the reader to "understand the architecture" or "explore the repository" with observable proof.

Move that background into links the task can call for.

### Put proof after each stage

A command exiting without an error only proves that the command exited. The database may still be unhealthy, the API may be pointed at the wrong environment, and the frontend may be serving a cached build.

The next block uses placeholder localhost ports and illustrative service commands:

```text
Database ready:  docker compose ps --format json
API ready:       curl --fail http://localhost:8080/health
Tests ready:     npm test
Frontend ready:  open http://localhost:3000
```

Write the expected signal beside each check. If `curl` returns a non-`200` response, stop the route and send the reader to the recovery block for the API.

Do not let step six become the place they discover that step two never worked.

## Give the reader one supported setup path

Setup pages collect commands like kitchen drawers collect dead batteries. A bootstrap script works for one person, Docker works for another, and an old wiki page still ranks in internal search.

Calling the pile "flexible" transfers maintenance decisions to the person with the least context.

Choose one supported route and mark it as the route the team tests. Put a required platform alternative under its own heading.

Move historical commands out of the main path.

### Expose versions and access before they block a command

"Install Node" is not an instruction. Name the version source, the verification command, and the first step that needs it.

[Corepack's maintained README](https://github.com/nodejs/corepack/blob/main/README.md) says the `packageManager` field records a supported manager and version. It documents `corepack enable [name]` for command shims and `corepack install` for the manager configured in the current project.

The dependency record below is illustrative. `pnpm@10.17.1`, the vault role, service file, and recovery commands are placeholders rather than facts about a repository.

| Dependency | Source of truth | Check | Failure branch |
| --- | --- | --- | --- |
| Node.js | `.node-version` | `node --version` | Run the repository's version-manager command |
| Package manager | `"packageManager": "pnpm@10.17.1"` in `package.json` | `pnpm --version` prints `10.17.1` | In a Corepack-managed repository, run `corepack enable pnpm` and `corepack install`; otherwise use the repository's documented installer |
| Test secrets | Test-vault role | `vault token lookup` | Request the role before cloning private fixtures |
| Local services | `compose.yaml` | `docker compose config --quiet` | Fix missing variables before starting containers |

Replace "ask the team" with a product or repository artifact before publishing the setup path.

Microsoft's [onboarding guide template](https://microsoft.github.io/code-with-engineering-playbook/developer-experience/onboarding-guide-template/) separates setup from contacts, team agreements, and project building blocks. It also says the guide can link to project material that already exists.

That is a useful boundary: the route should connect the right pages, not swallow the handbook.

<div class="visual-wrapper">
  <div class="visual-title">Microsoft's onboarding guide template</div>
  <div class="visual-container">
    <img src="/static/images/visuals/microsoft-onboarding-template.png" alt="Microsoft Engineering Fundamentals onboarding template with separate areas for goals, contacts, team agreements, setup, project building blocks, and resources" loading="lazy">
  </div>
</div>
<p class="visual-caption">Setup has a distinct job. Contacts and project context remain available without blocking the first run.</p>

### Attach recovery to the fragile step

"Ask in Slack if you get stuck" is an escape hatch for the document, not help for the engineer. Put the symptom, diagnostic, supported fix, and escalation owner beside the command that can fail.

The following `checkout-db` service, port, environment variable, and `#dev-help` channel are fictional placeholders:

```text
Symptom: checkout-db is unhealthy
Check:   docker compose logs checkout-db --tail=50
Cause:   Port 5432 is already used by a local PostgreSQL service
Fix:     Stop the local service or set CHECKOUT_DB_PORT=5433
Verify:  docker compose ps checkout-db
Escalate: Post the command and full output in #dev-help
```

Replace "restart everything" with the state to clear, the supported fix, and a verification command. Name a real escalation destination before the guide ships.

## Use the first change to teach how the team ships

The starter task is not free labor dressed as onboarding. Its job is to expose the team's real development loop while keeping the cost of a mistake small.

GitLab's public [onboarding handbook](https://handbook.gitlab.com/handbook/people-group/general-onboarding/) turns onboarding into issue tasks with ownership, a due date, and role-specific branches. That system is much larger than a first engineering change, but the useful idea survives at smaller scale: onboarding work is assigned work with a visible state.

<div class="visual-wrapper">
  <div class="visual-title">GitLab's public onboarding handbook</div>
  <div class="visual-container">
    <img src="/static/images/visuals/gitlab-onboarding-handbook.png" alt="GitLab handbook describing onboarding issue tasks, ownership, and role-specific work" loading="lazy">
  </div>
</div>
<p class="visual-caption">The task has an owner and a completion state. It is not a folder of optional reading.</p>

### Choose a change that is real and reversible

A suitable first issue travels through the normal branch, test, review, and deployment path without putting production data or credentials at risk.

Use this acceptance test:

- The change affects behavior a reader can observe.
- A failing test can describe the starting state.
- The change stays inside one owned component.
- The test environment can prove the result.
- Reverting the merge restores the earlier behavior.

If the issue needs access to production data, touches several services, or has no reliable test, it fails as an onboarding task even if the code diff is short.

### Delay architecture until the task gives it a hook

Give the reader the path of the request they exercised. The component chain below is illustrative, not an architecture claim:

```text
Browser -> API gateway -> authentication -> checkout service -> database
```

Link each component to its repository, local run command, and owner. Stop there.

The complete platform diagram can wait until the engineer has a request, a log line, and a code path to pin it to.

## Keep the route attached to product changes

An onboarding guide rots when setup changes travel through one workflow and the guide lives in another. The page still looks polished while each release moves it one command further from the product.

GitLab's [documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) strongly encourages documentation in the code merge request or in a separate merge request raised at the same time. Microsoft's [repository guidance](https://microsoft.github.io/code-with-engineering-playbook/documentation/guidance/project-and-repositories/) places setup, build, test, deployment, and working agreements with the project.

Both sources support the same practical move: review the route where maintainers can compare it with the change.

### Assign ownership at the point of change

Record the owner and update trigger for each stage. The roles in this table are illustrative.

Use the actual teams that control each fact:

| Stage | Owner | Review trigger |
| --- | --- | --- |
| Access | Platform team | Role or vault-policy change |
| Local setup | Service maintainer | Runtime, dependency, or container change |
| Starter issue | Product team | Workflow or test-harness change |
| Pull request | Repository maintainer | CI or review-policy change |
| Test deployment | Release owner | Environment or release-process change |

One person can own the complete route, but a generic "docs owner" cannot verify facts controlled by other teams. Name the fact owner beside each stage.

### Rerun the route from a clean state

A clean container catches missing packages. It cannot request a real permission, interpret an unclear issue, or notice that two pages disagree about the supported workflow.

Use automation for deterministic setup and a human route review for the decisions around it.

The next block uses the reserved `example.com` domain, a fictional `checkout-api` repository, placeholder localhost port `8080`, and illustrative commands. Do not copy it as a live setup path:

```bash
git clone https://example.com/checkout-api.git
cd checkout-api
mise install
docker compose up --detach
npm test
curl --fail http://localhost:8080/health
```

If the real run depends on a global package, cached credential, or private instruction absent from the page, repair the route before changing the success message.

## Test the method on a fictional checkout API

The following Orbit checkout service is a worked example, not a client story or a measured result. Its purpose is to make the review decisions concrete.

The weak issue says: "Read the architecture overview, clone the repositories, set up the services, and choose a starter ticket." Each instruction sounds reasonable.

Together they dump repository choice, setup state, task safety, and proof onto the new engineer.

### Replace the reading list with a route

| Stage | Instruction | Evidence |
| --- | --- | --- |
| Access | Join `checkout-dev` and request the test-vault role | The test secret is visible |
| Repository | Clone `checkout-api` and run `mise install` | `node --version` matches `.node-version` |
| Services | Run `docker compose up db redis` | Both services report `healthy` |
| API | Run `npm run dev`, then call `/health` | The response contains the current commit SHA |
| First request | Create a test checkout with the sample token | The response returns a checkout ID |
| First change | Reject an empty `customer_reference` | The new test fails, then passes after the change |
| Review | Open a pull request with the onboarding label | CI passes and the component owner reviews it |
| Deploy | Merge and call the test API | The validation error appears in the test environment |

This route teaches the product through the team's normal machinery. Replace any "looks right" evidence with output a reviewer can inspect.

### Audit decisions instead of page views

After someone uses the route, record the stage where they needed an undocumented choice or a rescue. Do not publish a made-up benchmark for "time to productivity."

| Observed failure | Documentation decision |
| --- | --- |
| The vault role is requested after setup blocks | Move access before the repository step |
| The health check passes against the wrong build | Return the commit SHA in the response |
| Starter issues cross component boundaries | Add ownership and rollback criteria |
| Review waits with no assignee | Name the reviewer in the onboarding issue |

Each observation should point to a repair in the route. Page views cannot tell you which undocumented decision stopped the reader.

## Developer onboarding docs checklist

- The route ends in one safe merged change through the normal delivery workflow.
- One supported setup path exposes prerequisites before commands.
- Each fragile stage has proof, recovery, and an escalation destination.
- Fact owners and product-change triggers are visible.
- A clean-state run reproduces the documented path.

Onboarding is one route inside a wider documentation package. The guide to [what technical documentation should include](/articles/what-is-technical-documentation-and-what-should-it-include/) shows which questions belong outside it.

Before the route ships, the [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) should attack the commands, assumptions, and rendered page.
