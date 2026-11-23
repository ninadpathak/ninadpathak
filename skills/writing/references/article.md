# How-to, explainer and search articles

The reader arrived with a question, and the title already told them this page answers it. Each part below has one job.

## Structure

```
# <Title: the literal phrase the reader typed>
(intro, no heading)
## TL;DR                      (when the query has a direct answer)
## What is <topic>?           (one or two short paragraphs)
## How to <do the thing>
    (lede paragraph)
    ### Step 1: <outcome>
    ### Step 2: <outcome>
## Edge cases, or what to do next
## Further reading             (only when real resources exist)
```

| Part | Its job | Fails when |
|---|---|---|
| Intro | Meet the reader where they stand and say what the piece walks through. Entries and models: [openings.md](openings.md). | It explains why the topic matters to someone who searched for it |
| TL;DR | The direct answer, as short bullets or a compact table in plain language | It holds prose paragraphs or fenced code |
| Quick definition | Align vocabulary in one or two short paragraphs, with the direct answer in the first sentence | It turns into history, or runs past two paragraphs |
| Steps | Each step is an H3 under one container H2, named for its outcome | Steps sit as top-level siblings, or a step opens with three paragraphs before code |
| Edge cases | The traps a reader hits after the happy path | Gotchas appear in the intro |

A how-to on a reference-style site uses a longer fixed order: intro, what the command is, syntax, how to use it, code examples with explanation, edge cases, conclusion, further reading. Set one structure per content type and keep it across the site.

## Intro registers

**Narrative intro.** For a piece that carries the author's experience, such as "How to build a software factory". Use the four moves in [openings.md](openings.md).

**Plain search intro.** For a reference page where the reader wants the command and nothing else. It has three parts in a spoken voice: why someone comes to this topic, the snag they hit, and the assurance that this page solves it. Ninad's calibrated example:

> If you've worked with MySQL, you've probably typed SHOW TABLES a hundred times. Try it in SQLite and you get a syntax error. SQLite does let you list your tables, it just does it differently, and in this article I'll walk you through every way to do it.

Origin stories for a comparison go in the first body section of a plain search page. Calibrate intros on a small sample with Ninad before rolling them out across many pages.

## Titles and headings

Set these before drafting. The title and headings are the part search engines and answer engines read first, so they are written plain and literal. The spoken voice lives in the body text under them, and it does not move into the headings.

- **Title.** Use the literal search phrase a reader would type, or very close to it. Put the primary keyword near the front, keep it between 50 and 65 characters, and write it plain: no clickbait, no colon-stuffed clever subtitles, no hype words, and no year unless the topic is time-bound.
- **H1.** It equals the title or matches it tightly.
- **H2s.** Make each one clear, literal and keyword-aware. Use question form where a reader would ask it ("What is X?", "How does X work?", "Why does X break?"), or a plain descriptive label ("How to set up X"). Keep each H2 specific, short (under about 60 characters), unique, and in logical order.
- **H3s.** Add them only when a section has parallel sub-steps.
- **No stacked headings.** Never put two headings back to back without a lede paragraph between them.
- **No cute headings.** A narrative-only heading such as "The Part Nobody Mentions" hides the keyword, so name the topic instead.
- **Answer first (hard rule).** The first paragraph under each H2 gives the direct answer in one or two sentences, and then the narrative walks through the why. Keep the connector voice while doing it. The test: read each H2 as the question, then read the first sentence under it. That sentence must answer that exact question in plain words before any background, definition of terms, or setup. If the heading asks what something shows, does, is or costs, the first sentence names the actual items, behaviour, definition or number. Background (clusters, catalogs, history) comes after the answer. If the first sentence would answer a different question, change the sentence or change the heading. Setup and signpost sentences ("So,", "Meanwhile,", "Now,", "Well,") are never the opening words of an answer-first paragraph: the answer comes first, and the setup budget applies after it.

A before and after, using the prompt caching sample topic:

- Weak title: "Your Agent Keeps Re-Reading Its Own Prompt, and Prompt Caching Decides What That Costs" (86 characters, and the reader has to decode it).
- Strong title: "How Prompt Caching Works in LLM APIs (and What It Costs)" (56 characters, keyword first).
- Weak H2: "The Part Nobody Mentions". Strong H2: "Why does prompt caching break?"

A before and after for answer first, under the H2 "What does listing PostgreSQL databases show?":

- Weak: "So, a PostgreSQL server cluster can hold several databases, and the pg_database system catalog stores one row for each. Meanwhile, the psql listing commands show names with owner and connection details, while a catalog query lets you filter or sort the names as SQL data." The heading asks what the list shows, and the first sentence talks about clusters and catalogs. It opens on a setup word, and the reader has to wait for the answer.
- Strong: "It shows each database's name, owner, encoding, collation and access privileges, plus its size with \l+. A cluster can hold several databases, and each row comes from the pg_database catalog." The first sentence names the items the heading asks about, and the cluster and catalog background follows.

## Body

- Each sentence builds on the one before it. Use tables, code blocks and bullets wherever they carry the explanation better than a paragraph.
- First person marks a deliberate choice: "To show you how this works, I will use an example of ...". It never claims invented habits or history.
- A concept is taught and never sold. Only a client product gets explained as a product, in its own section and in the same plain register.
- Public figures use USD. When the original work was priced in another currency, state the rate once.
- Terminal screenshots look like a real terminal: retina scale, a normal-weight monospace font, a hairline border and a title bar.

## Search and answer engines

- Match the average word count of the ten top-ranking pages within ten percent. The length comes from fuller coverage.
- Pull related and matching terms from Ahrefs or Semrush before drafting, and work the relevant ones in where they answer a real question.
- Use clear entity names, and put facts in tables and lists so an answer engine can lift them.
- On a refresh, change the post's publish date to the refresh date. An "Updated" line is never added.

## SEO finishing pass

Run this after the edit pass, as the final step. It touches links, title, headings and metadata only, and it does not rewrite the body voice.

1. **Internal links.** Add 3 to 6 contextual links to the site's own related articles, with natural descriptive anchor text (not "click here", and not the bare keyword every time). Place each one where a reader would want the next piece of information, spread through the body. Never put one in the first paragraph or in a heading, and never link the same URL twice. Check that each target URL actually exists, if the site is known or a sitemap or list is provided. If no site context is available, do not invent URLs. Output a list of suggested internal-link opportunities instead, each with proposed anchor text and the topic of the target article.
2. **External links.** Link primary sources (official docs, research) for key facts, with descriptive anchors, opening in the same tab, and no more links than needed.
3. **Metadata.** Write a meta description of 150 to 160 characters that includes the primary keyword and states what the reader gets. Write a URL slug that is short, lowercase, hyphenated and keyword-first. If images are planned, suggest alt text for them.
4. **Last read-through.** Confirm that the title, H2s and links obey the rules above, and that no link or heading disturbed the spoken flow.
