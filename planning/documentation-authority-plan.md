# Documentation Authority Content Plan

**Status:** Canonical strategy for the next six months  
**Created:** 2026-07-29  
**Supersedes:** The publishing direction in `content-strategy.md`, `growth-strategy.md`, and `post-queue.md`  
**Research source:** Semrush US database, collected 2026-07-29

## The position

NinadPathak.com should become the practical resource for DevTools and SaaS teams that
need to build documentation and technical content themselves.

The site should answer this question:

> How do we create documentation and technical blog content that developers can use,
> search engines can rank, and AI systems can retrieve accurately?

This position matches the paid work:

- Product, developer, SDK, CLI, and API documentation
- Technical tutorials and code examples
- SEO-friendly technical blog posts
- AI-search-friendly documentation and content

The site is not a technical-writing career resource. It does not need to target
"technical writing services," "technical writing jobs," courses, salaries, or generic
definitions written for aspiring writers.

## Ideal customer profile

### Company

- API-first SaaS, DevTools, AI infrastructure, developer platforms, and technical B2B SaaS
- Seed to Series C, or a larger product team with no mature documentation function
- Documentation hosted in Mintlify, Docusaurus, ReadMe, GitBook, Redocly, a custom static
  site, or Markdown in a repository

### Buyer or internal champion

- Head of Developer Relations or Developer Experience
- Documentation lead or technical content lead
- Product manager responsible for onboarding or API adoption
- Engineering manager whose team currently owns documentation
- Founder or marketing lead at an early-stage developer product

### Situation

They are trying to do the work themselves. An engineer, PM, DevRel person, or marketer
owns documentation in addition to another job. They search when:

- The documentation site has grown without a usable structure
- API reference pages exist but developers still cannot complete a task
- Code examples are incomplete, stale, or hard to copy
- Documentation does not rank for product or problem queries
- Google indexes the marketing site but ignores the docs subdomain
- An AI assistant retrieves the wrong section or misses the answer
- Documentation becomes stale after every release
- The team cannot measure whether documentation is helping
- They need to choose a documentation platform or docs-as-code workflow
- They need templates, checklists, or examples to ship the work quickly

## Strategy principles

1. **Target a job, not a writing term.** Every page must solve a documentation or
   technical-content task the ICP is actively trying to complete.
2. **Use one search intent per URL.** Do not publish multiple articles for keyword
   variations that belong on the same page.
3. **Show the artifact.** Templates, repositories, tested code, audits, raw results,
   and before-and-after examples are part of the article, not optional extras.
4. **Make every claim inspectable.** Cite official documentation and publish the method
   behind original tests. Do not invent personal experience, benchmark results, users,
   clients, or anecdotes.
5. **Build a reserve, then publish sequentially.** Prepare and review 10–15 articles
   locally before starting a release run. Publish one article every two days and never
   make the whole reserve live in one deployment. Evidence-heavy anchor pages run in
   parallel with narrower implementation guides, templates, checklists, and focused
   answers.
6. **Build around durable problems.** Tool comparisons can support the plan, but the
   core library must remain useful when vendors and model names change.
7. **Treat SEO and AI retrieval as product requirements.** Clear HTML, stable headings,
   direct answers, descriptive links, accessible code, and coherent information
   architecture help both humans and retrieval systems.

## Keyword findings

Semrush volume is directional, not a publishing order by itself. Broad keywords can be
ambiguous, and zero-volume phrases can still represent valuable buyer problems. The plan
prioritizes the overlap between measurable demand, ICP relevance, achievable difficulty,
and the opportunity to publish original evidence.

### Core opportunities

| Keyword cluster | US volume | KD | Why it matters |
|---|---:|---:|---|
| technical documentation template | 480 | 26 | High-intent DIY task and natural downloadable asset |
| technical documentation example/sample | 390-480 | 30-36 | Lets us teach by teardown rather than generic advice |
| technical documentation best practices | 140 | 25 | Strong foundation page for the whole site |
| how to write technical documentation | 210 | 41 | Can be satisfied by the best-practices and template cluster |
| API documentation tools | 480 | 28 | Buyer-relevant comparison with strong CPC |
| API documentation example | 390 | 28 | Practical and directly connected to paid work |
| API documentation best practices | 260 | 31 | Core API documentation authority page |
| API documentation template | 210 | 19 | Achievable and asset-led |
| how to write API documentation | 140 | 33 | Belongs on the best-practices page, not a separate article |
| docs as code / documentation as code | 320 | 28-31 | Exact workflow used by the ICP |
| technical documentation software | 590 | 23 | Tool evaluation for teams building docs themselves |
| software documentation tools | 210 | 28 | Supporting tool-intent cluster |
| documentation maintenance | 90 | 3 | Small volume, excellent ICP fit and low competition |
| documentation automation | 170 | 34 | Connects docs-as-code, CI, and AI-assisted workflows |
| troubleshooting guide template | 170 | 5 | High-value documentation format with attainable difficulty |
| developer onboarding checklist | 70 | 8 | Direct pain point and downloadable asset |
| code documentation best practices | 140 | 36 | Connects documentation and code examples |
| AI code documentation | 110 | 25 | Useful AI-assisted documentation topic without becoming an AI news site |
| documentation metrics | 40 | 9 | Small volume, strong conversion and expertise signal |
| SEO documentation | 260 | 37 | Closest measurable term to the core SEO-for-docs position |
| llms.txt generator | 2,400 | 35 | Tool opportunity with meaningful demand |
| what is llms.txt | 590 | 48 | Supporting guide and experiment, not a speculative claim page |
| llms.txt example(s) | 260-480 | 40-42 | Can be covered by the generator and implementation guide |
| semantic chunking | 390 | 33 | Strong bridge between documentation structure and AI retrieval |
| chunking strategy for RAG | 70 | 48 | Best addressed through an original documentation-corpus benchmark |
| SEO content brief | 590 | 28 | Template opportunity for the technical-blog side of the service |
| technical content marketing | 170 | 12 | Relevant supporting pillar for developer-facing blog content |
| B2B SaaS content strategy | 140 | 19 | Use only with a technical/developer-product angle |

### Keywords intentionally excluded

- Technical writing services, agencies, jobs, salaries, courses, certifications, and careers
- The ambiguous 1.83M "technical documentation" head term
- Vendor documentation queries where the user wants the vendor's official docs
- Generic AI SEO, GEO, and AEO head terms with high difficulty and weak documentation intent
- AI-agent architecture topics that do not connect directly to documentation retrieval
- Separate pages for every `llms.txt`, docs-as-code, or API-documentation keyword variation

## Site architecture

Keep the public structure compact until the corpus earns enough demand to justify more
landing pages:

| Content type | Public location | What belongs there |
|---|---|---|
| Editorial content | `/articles/` | Documentation, DevRel, developer education, tutorials, technical writing, and essays |
| Tools and software | `/projects/` | Interactive generators, checkers, applications, and working software |
| Reusable assets | `/resources/` | Templates, playbooks, checklists, ebooks, courses, and downloads |

The six documentation clusters remain internal editorial planning categories. They are
not cards, filters, or separate hub URLs on the public Articles page. `/articles/` is a
plain blog index with a short introduction followed by the published article list.

`/resources/` remains unpublished and absent from navigation until the first complete
asset passes review. New subsections should be created only when the content inventory,
search demand, and user navigation needs justify them.

## Six-month publishing plan

The plan contains 90 releases: 18 evidence-heavy anchors and 72 focused supporting
pieces. Each month has 15 publication slots, or roughly one new page every two days.

The three anchors in each month establish the cluster. The 12 supporting pages answer
one narrower task each and link back to the relevant anchor. Support pages are not
permission to split synonyms into separate URLs. When two ideas satisfy the same intent,
they belong on one page.

### Month 1: Establish the documentation position

#### 1. SEO for Technical Documentation: The Complete Developer Docs Checklist

- **Primary cluster:** SEO documentation
- **Volume / KD:** 260 / 37
- **Intent:** Build or repair a documentation site's organic discoverability
- **Format:** Data-backed guide
- **Required evidence:** Audit at least 20 real DevTools documentation sites for
  indexability, canonical behavior, titles, internal linking, rendering, sitemaps, and
  structured data. Publish the methodology and anonymized results table.
- **Conversion bridge:** Documentation SEO audit

#### 2. Technical Documentation Template: From Empty Repository to Published Guide

- **Primary keyword:** technical documentation template
- **Volume / KD:** 480 / 26
- **Secondary terms:** format for technical documentation, technical document template
- **Format:** Working template plus tutorial
- **Required evidence:** Public GitHub template with example Markdown, navigation,
  frontmatter, review checklist, and a deployable Docusaurus or static-site example
- **Conversion bridge:** Documentation architecture and writing help

#### 3. Technical Documentation Best Practices, Tested on Real Developer Docs

- **Primary keyword:** technical documentation best practices
- **Volume / KD:** 140 / 25
- **Secondary term:** documentation best practices, 110 / 36
- **Format:** Evidence-led foundation page
- **Required evidence:** Before-and-after examples, real broken workflows, and references
  to official platform documentation. Avoid unsupported universal rules.
- **Existing-content action:** Replace and redirect
  `technical-writing-for-engineers` and merge the useful argument from
  `the-case-for-shorter-technical-documentation`.

#### Month 1 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | What Is Technical Documentation, and What Should It Include? | Understand the deliverables before starting |
| 5 | Types of Technical Documentation: Choose the Right Format | Match tutorials, how-to guides, reference, and explanation to a task |
| 6 | Internal vs. External Documentation: What Belongs Where | Separate team knowledge from customer-facing docs |
| 7 | How to Organize a Documentation Site | Turn an unstructured page list into usable navigation |
| 8 | Documentation Information Architecture for Developer Products | Design hierarchy, labels, and cross-links |
| 9 | Documentation Style Guide Template for Developer Teams | Standardize terminology, voice, code, and UI references |
| 10 | Documentation Review Checklist Before You Publish | Run an editorial, technical, and usability review |
| 11 | Documentation Accessibility Checklist | Make headings, code, links, tables, and visuals accessible |
| 12 | How to Write Task-Based Documentation Headings | Replace topic labels with scannable reader tasks |
| 13 | What a Documentation Homepage Must Help Users Do | Design a useful entry point rather than a card wall |
| 14 | How to Audit Broken Links, Redirects, and Canonicals in Docs | Find crawl and migration defects |
| 15 | How to Document Multiple Product Versions | Prevent users and search engines from landing on the wrong version |

### Month 2: Own practical API documentation

#### 4. API Documentation Best Practices: Reference, Guides, and Working Requests

- **Primary keyword:** API documentation best practices
- **Volume / KD:** 260 / 31
- **Secondary terms:** how to write API documentation, how to document an API
- **Format:** Working API documentation system
- **Required evidence:** Build documentation for a small sample API, including
  authentication, endpoint reference, errors, pagination, webhooks, and runnable requests
- **Conversion bridge:** API documentation projects

#### 5. API Documentation Examples: What the Best Developer Portals Get Right

- **Primary keyword:** API documentation example
- **Volume / KD:** 390 / 28
- **Secondary term:** API documentation examples, 140 / 38
- **Format:** Teardown of 8-10 real documentation experiences
- **Required evidence:** Screenshots, repeatable scoring rubric, and task completion tests
- **Guardrail:** Do not turn this into a subjective gallery

#### 6. API Documentation Tools: A Hands-On Comparison for Small Teams

- **Primary keyword:** API documentation tools
- **Volume / KD:** 480 / 28
- **Secondary terms:** best API documentation tool, API documentation software
- **Format:** Tested comparison
- **Required evidence:** Build and publish the same sample API in at least five tools.
  Score setup, OpenAPI support, code samples, search, versioning, Git workflow, SEO
  controls, and exportability.
- **Update policy:** Re-test every six months; never change the date without re-testing

#### Month 2 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | API Documentation Template: The Pages Every API Needs | Start an API docs project from a complete outline |
| 5 | What Is API Documentation? Reference, Guides, and Examples | Understand the components of an API docs system |
| 6 | API Reference vs. API Guides: Where Each Answer Belongs | Stop forcing every task into endpoint reference pages |
| 7 | How to Document API Authentication | Explain keys, OAuth, scopes, expiry, and failed authentication |
| 8 | How to Document API Errors | Turn codes and messages into actionable recovery steps |
| 9 | How to Document API Pagination | Show cursors, limits, ordering, and complete iteration |
| 10 | How to Document Webhooks | Cover payloads, signing, retries, ordering, and testing |
| 11 | How to Write API Code Examples Developers Can Run | Produce complete requests with expected responses |
| 12 | REST API Documentation Example: A Complete Endpoint | Show one endpoint from authentication through errors |
| 13 | OpenAPI Documentation Best Practices | Improve descriptions, examples, schemas, and generated output |
| 14 | Interactive API Documentation: When Try-It Consoles Help | Decide when interactivity improves or harms the workflow |
| 15 | API Documentation Checklist Before Release | Verify coverage, accuracy, examples, and version behavior |

### Month 3: Build the docs-as-code operating system

#### 7. Docs as Code: A Working Git-Based Documentation Workflow

- **Primary keyword:** docs as code
- **Volume / KD:** 320 / 31
- **Secondary term:** documentation as code, 320 / 28
- **Format:** End-to-end implementation
- **Required evidence:** Public repository with branches, preview builds, pull-request
  reviews, linting, link checks, and Cloudflare Pages deployment
- **Existing-content action:** Use this site's generator as one implementation example,
  including what failed and what was fixed

#### 8. Technical Documentation Software: How to Choose Without Replatforming Twice

- **Primary keyword:** technical documentation software
- **Volume / KD:** 590 / 23
- **Secondary terms:** software documentation tools, documentation tools
- **Format:** Decision framework plus tested shortlist
- **Required evidence:** A decision matrix based on team size, content type, Git support,
  API reference needs, localization, SEO controls, portability, and total maintenance cost
- **Cannibalization rule:** This page chooses platforms; the API-tools article tests API
  documentation workflows specifically

#### 9. Documentation Maintenance: A Workflow That Keeps Docs Current

- **Primary keyword:** documentation maintenance
- **Volume / KD:** 90 / 3
- **Secondary terms:** maintain documentation, documentation workflow
- **Format:** Operational playbook
- **Required evidence:** GitHub issue templates, ownership matrix, freshness metadata,
  release trigger, stale-page report, and review schedule
- **Conversion bridge:** Ongoing documentation maintenance

#### Month 3 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | Docs-as-Code Tools: The Minimum Stack You Actually Need | Choose authoring, preview, linting, and deployment tools |
| 5 | Docs-as-Code Example Repository, Explained File by File | Understand a working repository without copying blindly |
| 6 | Documentation Workflow From Issue to Published Page | Define ownership and handoffs |
| 7 | Documentation Automation That Is Safe to Trust | Automate mechanical work without inventing content |
| 8 | Automated API Documentation From OpenAPI | Generate reference while preserving human-written guidance |
| 9 | Documentation Testing: What You Can Validate in CI | Test links, structure, spelling, code, and builds |
| 10 | Documentation Linting With Vale and Markdownlint | Enforce useful rules without fighting every sentence |
| 11 | How to Add a Broken-Link Check to Documentation CI | Catch dead internal and external links before release |
| 12 | Preview Deployments for Documentation Pull Requests | Let reviewers inspect the rendered change |
| 13 | Documentation Versioning in Git | Align product, branch, and published documentation versions |
| 14 | Documentation Ownership: A Practical Maintainer Model | Assign accountable owners without creating a bottleneck |
| 15 | Documentation Migration Checklist | Move platforms without losing URLs, metadata, or search equity |

### Month 4: Teach the formats teams struggle to write

#### 10. Technical Documentation Examples: Tutorials, How-To Guides, Reference, and Explanation

- **Primary keyword:** technical documentation example
- **Volume / KD:** 480 / 36
- **Secondary terms:** technical documentation sample, documentation example
- **Format:** Original examples built around one sample product
- **Required evidence:** Four complete documents for the same product, not screenshots
  copied from other sites
- **Framework:** Use Diátaxis where it helps, but test the framework against real tasks

#### 11. Troubleshooting Guide Template: Write Answers Developers Can Actually Use

- **Primary keyword:** troubleshooting guide template
- **Volume / KD:** 170 / 5
- **Secondary term:** troubleshooting documentation
- **Format:** Template plus worked example
- **Required evidence:** Symptom-to-cause decision tree, exact error messages, diagnostic
  commands, expected output, rollback instructions, and escalation criteria

#### 12. Developer Onboarding Checklist for API and DevTools Products

- **Primary keyword:** developer onboarding checklist
- **Volume / KD:** 70 / 8
- **Secondary terms:** developer onboarding documentation, developer onboarding best practices
- **Format:** Checklist plus onboarding test
- **Required evidence:** Time a new user completing a sample integration, document every
  failure, then show the revised onboarding path
- **Existing-content action:** Rebuild
  `developer-onboarding-docs-what-works-what-doesnt` on its current URL if the intent
  remains aligned

#### Month 4 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | Tutorial vs. How-To vs. Reference vs. Explanation | Choose the right document type for the reader task |
| 5 | How to Write a Technical Tutorial That Survives Copy-Paste | Build and test a complete learning path |
| 6 | How-To Documentation Template | Write a focused procedure for a known goal |
| 7 | Reference Documentation Template | Record parameters, behavior, constraints, and examples consistently |
| 8 | How to Write Explanation Documentation | Teach concepts and tradeoffs without hiding the task pages |
| 9 | Release Notes Best Practices for Developer Products | Communicate impact, action required, and migration details |
| 10 | Changelog Best Practices: Structure, Links, and Automation | Maintain a useful chronological product record |
| 11 | How to Write an API Changelog | Track breaking changes, deprecations, and new behavior |
| 12 | SDK Documentation Best Practices | Document installation, initialization, methods, and language differences |
| 13 | CLI Documentation Best Practices | Cover commands, flags, output, exit codes, and shell examples |
| 14 | README Best Practices for Developer Tools | Get users from repository landing page to first success |
| 15 | How to Document Error Messages | Connect exact messages to causes, fixes, and escalation |

### Month 5: Make documentation retrievable by AI systems

#### 13. Free `llms.txt` Generator and Checker for Documentation Sites

- **Primary keyword:** llms.txt generator
- **Volume / KD:** 2,400 / 35
- **Secondary terms:** generate llms.txt, llms.txt checker, llms.txt example
- **Format:** Free tool with a concise guide
- **Required evidence:** Validate generated output, expose every rule used, and provide
  example files for at least three documentation-site structures
- **Guardrail:** Do not claim that the file guarantees inclusion or ranking in AI answers

#### 14. Does `llms.txt` Improve AI Visibility? A Controlled Documentation Test

- **Primary question:** will llms.txt help your SEO
- **Volume / KD:** 110 / 54
- **Supporting questions:** does llms.txt work, how to use llms.txt
- **Format:** Time-bound experiment
- **Required evidence:** Pre-register the test, compare matched documentation sets,
  record crawler access and answer citations over time, publish null results if nothing
  changes
- **Cannibalization rule:** The generator handles implementation; this page handles evidence

#### 15. Semantic Chunking for Documentation RAG: A Reproducible Benchmark

- **Primary keyword:** semantic chunking
- **Volume / KD:** 390 / 33
- **Secondary terms:** chunking strategy for RAG, document chunking
- **Format:** Reproducible benchmark
- **Required evidence:** Public corpus, chunking code, retrieval queries, relevance labels,
  raw JSON/CSV, and evaluation notebook. Compare heading-aware, fixed-token, recursive,
  and semantic chunking.
- **Existing-content action:** Reuse only verified material from the RAG cluster

#### Month 5 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | What Is `llms.txt`, and What Is It Not? | Understand the proposal without inflated promises |
| 5 | `llms.txt` Format and Implementation Guide | Create and validate a file manually |
| 6 | `robots.txt` for AI Crawlers: A Documentation-Site Guide | Decide which crawlers can access which content |
| 7 | AI-Ready Documentation Checklist | Improve structure and retrievability without keyword theater |
| 8 | Document Chunking Strategies for RAG | Choose a chunking method for a documentation corpus |
| 9 | Heading-Aware Chunking for Technical Documentation | Preserve task and section context during retrieval |
| 10 | Fixed-Token vs. Recursive vs. Semantic Chunking | Understand the operational tradeoffs before benchmarking |
| 11 | Metadata for Documentation RAG | Attach product, version, language, and page-type filters |
| 12 | Hybrid Search for Documentation | Combine exact error-code matching with semantic retrieval |
| 13 | Reranking Documentation Search Results | Improve ordering after initial retrieval |
| 14 | How to Evaluate a Documentation Chatbot | Build answer, citation, refusal, and freshness tests |
| 15 | AI Chatbot for Documentation: A Reference Architecture | Connect ingestion, retrieval, generation, citations, and feedback |

### Month 6: Connect documentation and technical blog content

#### 16. Code Documentation Best Practices: Comments, Examples, and Reference Pages

- **Primary keyword:** code documentation best practices
- **Volume / KD:** 140 / 36
- **Secondary terms:** code documentation, self-documenting code
- **Format:** Repository-based guide
- **Required evidence:** One small codebase documented badly and well, generated reference
  output, copy-paste tests, and clear criteria for comments versus external docs

#### 17. SEO Content Brief Template for Technical Blog Posts

- **Primary keyword:** SEO content brief
- **Volume / KD:** 590 / 28
- **Secondary terms:** technical content brief, blog SEO checklist
- **Format:** Downloadable brief plus worked DevTools example
- **Required evidence:** Show the SERP analysis, reader task, technical test plan,
  code-validation requirements, internal-link map, and update trigger
- **Conversion bridge:** SEO-focused technical blog writing

#### 18. Documentation Metrics: How to Measure Whether the Docs Work

- **Primary keyword:** documentation metrics
- **Volume / KD:** 40 / 9
- **Secondary terms:** documentation quality, documentation audit
- **Format:** Measurement framework and dashboard template
- **Required evidence:** Define task success, failed searches, time to first successful
  request, support deflection, stale-page rate, code-example failures, and assisted
  conversions. Include implementation examples rather than invented benchmarks.
- **Existing-content action:** Salvage only supported material from
  `engineering-velocity-documentation`

#### Month 6 supporting releases

| Slot | Working title | Distinct reader job |
|---:|---|---|
| 4 | How to Write a Technical Blog Post for Developers | Turn a technical reader task into a credible article |
| 5 | Technical Blog Examples: Tutorials, Benchmarks, and Teardowns | Choose a format based on the evidence available |
| 6 | How to Write Code Examples for Technical Content | Make snippets complete, focused, and testable |
| 7 | Runnable Code Examples: A Validation Workflow | Test dependencies, setup, output, cleanup, and failure paths |
| 8 | Should This Be Documentation or a Blog Post? | Put durable product guidance and discovery content in the right place |
| 9 | Technical Content Marketing for Developer Products | Build trust and demand without disguising marketing as engineering |
| 10 | B2B SaaS Technical Content Strategy | Connect problem-led content, product proof, and conversion |
| 11 | Blog SEO Checklist for Technical Articles | Validate intent, structure, metadata, links, and page experience |
| 12 | How to Write a Developer Tutorial With a Real Test Environment | Design a reproducible build rather than decorative code |
| 13 | Technical Content Maintenance: When and How to Update | Set triggers for versions, rankings, links, and factual changes |
| 14 | How to Measure Technical Content Performance | Track qualified discovery, product usage, links, and assisted leads |
| 15 | How to Turn Documentation Research Into a Technical Blog Post | Repackage evidence without duplicating the documentation page |

## Backlog after the first 90 releases

These are valid extensions, but they should ship only after Search Console data shows
which first-six-month clusters are earning impressions and links:

1. Product documentation best practices (50 volume, KD 20)
2. SaaS documentation architecture (50, KD 9)
3. User manual documentation with a worked product example
4. Multi-product documentation strategy
5. Documentation localization workflow
6. GraphQL API documentation patterns
7. gRPC documentation patterns
8. API deprecation and migration guides
9. Python documentation generators tested on one package (110, KD 34)
10. AI code documentation tools tested on one repository (110, KD 25)
11. Documentation feedback systems
12. Failed-search analysis for documentation sites
13. Documentation search analytics
14. Developer portal design patterns
15. Documentation for command-line output and exit codes
16. Documentation for asynchronous jobs and event-driven APIs

## Existing-content migration

Do not delete or redirect the corpus in one deployment. First export Search Console and
backlink data, then process URLs in batches.

### Rebuild or merge into the new authority library

| Existing URL | Action |
|---|---|
| `technical-writing-for-engineers` | Replace with technical documentation best practices and 301 only if the final intent is equivalent |
| `technical-writing-for-ai-products-the-new-rules` | Rebuild as AI-ready documentation after factual research |
| `the-case-for-shorter-technical-documentation` | Merge useful material into documentation best practices |
| `developer-onboarding-docs-what-works-what-doesnt` | Rebuild around the onboarding checklist and timed test |
| `how-to-write-a-technical-tutorial-that-actually-teaches` | Keep, verify, and connect to code examples and documentation formats |
| `how-to-write-a-changelog-developers-actually-read` | Keep for the later release-management cluster |
| `writing-release-notes-that-developers-trust` | Keep and update against the best-practices keyword |
| `engineering-velocity-documentation` | Replace unsupported claims; merge into documentation metrics |
| `rag-evaluation-metrics-what-actually-matters` | Retain only after factual and evidence review; support the retrieval benchmark |
| `reranking-in-rag-why-your-top-k-results-are-probably-wrong` | Retain only if tested and relevant to documentation retrieval |
| `hybrid-search-bm25-vector-search` | Retain only if tested and relevant to documentation search |
| `embedding-models-compared` | Retain only if reproducible and needed by the retrieval cluster |
| `structured-outputs-llms-json-mode-function-calling` | Keep only if it supports API/code-example documentation |
| `how-anthropics-contextual-retrieval-changes-rag-architecture` | Reframe around documentation retrieval after verification |

### Move out of the SEO library or retire

The opinion-led posts about content moats, developer trust, Stripe's blog, becoming a
writer, and docs losing deals can remain as a small `/essays/` or `/about/` collection.
They should not define the SEO architecture.

Most agent memory, model inference, voice-agent, coding-model, and generic RAG articles
should be retired unless they directly support documentation retrieval and pass a fresh
factual review. Unrelated retired URLs should return 410 or a real 404. Never redirect
them all to `/documentation/` or the homepage.

### Glossary

Retire the 25-page AI glossary as a batch content strategy. Keep an entry only when it:

- Supports a published documentation article
- Has measurable or strategically important reader demand
- Cites primary sources
- Includes a concrete documentation example
- Is maintained when the underlying standard changes

Potential terms to rebuild later include semantic chunking, reranking, HyDE, bi-encoders,
OpenAPI, docs as code, developer portal, and `llms.txt`. Publish them individually, not
as a same-day batch.

### Portfolio and case studies

Keep the portfolio and case studies, but correct the traffic arithmetic, remove broken
links, and attach evidence that can be shared publicly. These pages support trust even
when they are not organic-traffic targets.

## Content specification

Every release must include the search, usability, retrieval, and conversion requirements
below. Evidence requirements scale with the claim: a focused answer needs verified
examples and primary sources; a benchmark needs the complete method and raw results.

### Search and intent

- One primary keyword cluster and one clearly stated reader job
- A current SERP review before outlining
- A statement explaining why the page deserves to exist beyond the current results
- A cannibalization check against every existing URL

### Technical evidence

- A public or inspectable artifact for anchors, templates, tools, and implementations
- Exact environment, versions, commands, and assumptions whenever a test is involved
- Raw results whenever the page reports a benchmark or original measurement
- Links to primary sources and official documentation
- A "last verified" date for version-sensitive claims
- Explicit separation between observed results, sourced facts, and opinion

### Human usability

- Direct answer or usable starting point near the top
- No prose paragraph contains more than two sentences
- Use first person for genuine opinions, decisions, and experience, not as paragraph scaffolding
- Do not restate a heading in the sentence below it or narrate an obvious checklist
- Keep the voice relaxed and spoken around precise technical claims
- Use human connectors when one thought follows another; not every sentence needs to stand alone
- Let context carry the subject instead of repeating the full noun or forcing unnecessary specificity
- Use the opening to challenge an existing decision, expose its cost, or give the reader a revealing test
- Do not spend the introduction calmly describing how a problem tends to happen
- Keep the hook to two short paragraphs: the moment, then the promise
- Use recognizable patterns in hooks; never invent page counts, dates, labels, or other reader specifics
- Avoid contrast formulas such as "not X, but Y"; keep the reader inside the situation and move forward
- Prefer simple words, concrete observations, and explicit opinions over corporate prose
- Let search intent choose the problem, never the personality of the writing
- Descriptive H2/H3 hierarchy with valid Markdown
- Copyable code with expected output and failure handling
- Tables only where they improve comparison
- Accessible visuals with a textual explanation
- Links that describe the destination

### Search and AI retrieval

- Self-referencing canonical and indexable server-rendered HTML
- Concise title and description matched to intent
- Stable, descriptive URL
- Breadcrumbs and relevant article schema
- Contextual internal links to `/articles/` and two genuinely related pages
- Sections that remain understandable when retrieved independently
- No unsupported claims that schema or `llms.txt` guarantees AI citations

### Conversion

- One contextual CTA tied to the task, such as an audit, implementation, rewrite, or
  maintenance engagement
- No generic sales interruption before the reader receives the answer
- A related portfolio example when one exists

## Publication and maintenance cadence

### Every-other-day publishing schedule

Publish on days 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, and 29 of each
month. The schedule is a pipeline, not a requirement to research and write every page
from scratch in 48 hours.

Each month contains three production tiers:

| Tier | Pages per month | Typical lead time | Appropriate formats |
|---|---:|---:|---|
| Anchor | 3 | 10-20 days | Original audits, tested comparisons, tools, benchmarks, complete templates |
| Practical | 5 | 3-6 days | Implementations, worked examples, format guides, operational playbooks |
| Focused | 7 | 1-3 days | One-question answers, checklists, narrow patterns, specific failure fixes |

Anchor work begins several weeks before its publication slot. Practical and focused
pages are batched around the same sample products and repositories so research, code,
screenshots, and terminology can be reused without duplicating prose or intent.

### Two-day release loop

1. **Day A morning:** Confirm intent, inspect the current SERP, and check cannibalization.
2. **Day A afternoon:** Draft from already verified cluster research and artifacts.
3. **Day B morning:** Verify sources, code, links, headings, metadata, and claims.
4. **Day B afternoon:** Render on mobile and desktop, publish, submit in Search Console,
   and add contextual links from the hub and relevant sibling pages.
5. **Following cycle:** Record indexing and query data while the next prepared piece ships.

Deep experiments do not fit inside this loop. Their research and testing run in the
anchor pipeline until the evidence is ready. If an anchor misses its slot, publish a
prepared focused piece instead. Never publish unfinished benchmark claims to protect
the calendar.

### Weekly maintenance alongside publishing

- Fix or consolidate at least two existing pages
- Review new internal links for usefulness and anchor clarity
- Respond to relevant community questions without dropping links indiscriminately
- Record impressions, queries, indexing state, backlinks, and conversions
- Re-test code and tool comparisons when dependencies change
- Keep at least seven fully reviewed pieces in the ready queue

### Publishing gate

A page does not ship when:

- The experiment or code cannot be reproduced
- A numerical claim has no source or raw result
- The topic duplicates an existing page's intent
- The page exists only because a keyword tool returned a phrase
- The reader would still need another search to complete the task
- The title promises a test, benchmark, template, or example that the page does not provide

## Measurement

Measure the plan by page and cluster, not by total article count.

### Leading indicators

- Valid indexed pages and crawl errors
- Search impressions for the intended query cluster
- Number of ranking queries per page
- Non-branded clicks
- Referring domains earned by templates, tools, and original tests
- Template downloads, GitHub stars/clones, and tool usage
- Assisted contact and booking conversions

### Review windows

- **14 days:** Check indexability and unexpected queries
- **45 days:** Improve snippets, internal links, and missing sections using Search Console data
- **90 days:** Decide whether to update, consolidate, or continue distributing
- **180 days:** Re-run tool comparisons and version-sensitive experiments

Do not declare a page a failure after a week, and do not publish another page merely to
make the site look active.

## First execution sequence

Before the first new release:

1. Add a real top-level `404.html` so Cloudflare Pages stops serving the homepage for
   nonexistent URLs.
2. Build a redirect/410 map for old and retired URLs.
3. Correct or temporarily unpublish factually unreliable articles.
4. Fix malformed headings, missing assets, broken portfolio links, and identity URLs.
5. Export Search Console page and query data.
6. Create the `/documentation/` and `/documentation-seo/` hubs.
7. Begin the 20-site documentation SEO audit for Release 1.

The unpublished `technical-writing-examples` draft should not ship in its current form.
The stronger replacement is Release 10, which targets technical documentation examples
and includes complete, original artifacts for one sample developer product.
