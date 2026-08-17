/*
 * AI Overviews extractability checker — rule engine.
 *
 * Pure functions only. No DOM, no network, no globals beyond the export, so the
 * browser and tests/test_aio_checker.py (through node) run the same code.
 *
 * WHAT THIS TOOL CLAIMS, AND WHAT IT DOES NOT
 *
 * It does not predict whether a page will appear in an AI Overview. Nobody can:
 * Google states there are "no additional requirements to appear in AI Overviews
 * or AI Mode, nor other special optimizations necessary"
 * (developers.google.com/search/docs/appearance/ai-features, last updated
 * 2025-12-10). Any tool claiming a probability is inventing one.
 *
 * What it does is check whether a page's *structure* makes its answers easy to
 * lift as a self-contained passage, which is the mechanism by which any answer
 * engine quotes anything. Each check therefore reports a status and the source
 * it rests on, and says whether it is a hard requirement or a heuristic.
 *
 * There is deliberately no weighted score. Checks are counted, not weighted,
 * because weights would imply a calibration nobody has. `confidence` is either:
 *   "documented" — the check restates something a primary source states outright.
 *   "heuristic"  — a text pattern that correlates with the property, and can be
 *                  wrong on any individual page. Never presented as a verdict.
 *
 * Sources, all dated, all primary:
 *   [G-AIO]  developers.google.com/search/docs/fundamentals/ai-optimization-guide
 *            "Google's Guide to Optimizing for Generative AI Features on Google
 *            Search", last updated 2026-07-10.
 *   [G-AIF]  developers.google.com/search/docs/appearance/ai-features,
 *            last updated 2025-12-10.
 *   [G-HC]   developers.google.com/search/docs/fundamentals/creating-helpful-content,
 *            last updated 2025-12-10.
 *   [QRG]    Google Search Quality Rater Guidelines, 182pp, PDF CreationDate
 *            2025-09-10 (verified from the live file 2026-08-17).
 *   [NNG-LC] Kara Pernice, "Text Scanning Patterns: Eyetracking Evidence",
 *            Nielsen Norman Group, 2019-08-25.
 *   [NNG-IP] Amy Schade, "Inverted Pyramid: Writing for Comprehension", NN/g,
 *            2018-02-11.
 *   [OBS]    First-party observation recorded in
 *            planning/research/seo-state-of-play-2026-08.md, 2026-08-17: the
 *            structure of a low-authority page Google cited in its AI Overview
 *            for `docs as code`.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AioCheckerCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var PASS = "pass";
  var ATTENTION = "attention";
  var INFO = "info";
  var SKIPPED = "skipped";

  var DOCUMENTED = "documented";
  var HEURISTIC = "heuristic";

  /* Openings that establish a topic instead of answering it. [NNG-IP] */
  var PREAMBLE_PATTERNS = [
    /^in (?:today|this day)/i,
    /^in the (?:world|landscape|era|age) of/i,
    /^(?:as|now) (?:more|most) (?:and more )?(?:companies|teams|developers|businesses)/i,
    /^(?:whether|if) you(?:'re| are) a/i,
    /^before we (?:dive|begin|get started|jump)/i,
    /^in this (?:article|post|guide|tutorial)/i,
    /^(?:today|here),? we(?:'ll| will)/i,
    /^let(?:'s| us) (?:dive|explore|take a look|begin|start)/i,
    /\bhas become (?:increasingly|more) (?:important|popular|common)\b/i,
    /\bis (?:one of )?the most important (?:aspects?|parts?|things?)\b/i,
    /\bin recent years\b/i,
    /\bfast-paced\b/i,
    /\bever-(?:evolving|changing|growing)\b/i,
    /\brapidly (?:evolving|changing|growing)\b/i
  ];

  /* Bare topic labels: a heading that names a subject without asserting or asking
   * anything. A layer-cake reader sees only headings, so a label transfers
   * nothing. [NNG-LC] */
  var TOPIC_LABEL_WORDS = [
    "overview", "introduction", "intro", "background", "basics", "fundamentals",
    "considerations", "best practices", "tips", "conclusion", "summary",
    "getting started", "features", "benefits", "use cases", "tooling", "tools",
    "structure", "versioning", "configuration", "setup", "architecture",
    "requirements", "prerequisites", "faq", "faqs", "resources", "references",
    "next steps", "final thoughts", "wrapping up", "key takeaways", "takeaways",
    "the basics", "what's next", "about", "details", "notes", "misc",
    "miscellaneous", "other", "advanced", "advanced topics", "examples"
  ];

  var VERB_HINT = /\b(?:is|are|was|were|be|has|have|had|do|does|did|can|cannot|can't|should|shouldn't|must|will|won't|need|needs|use|uses|used|make|makes|keep|keeps|write|writes|choose|choosing|pick|avoid|stop|start|beats|wins|fails|breaks|costs|means|belongs|goes|lives|gets|gives|tells|shows|prove|proves|add|adds|remove|removes|fix|fixes|treat|treats|run|runs|set|sets|put|puts|leave|leaves|send|sends|read|reads|reduce|reduces|replace|replaces|require|requires|prefer|prefers|ship|ships|test|tests|measure|measures|document|documents)\b/i;

  var PRONOUN_OPENERS = /^(?:it|this|that|these|those|they|them|there|he|she|his|her|its|such|both|either|neither|the former|the latter|another|the same)\b/i;

  var HEDGE_SOURCE_MARKERS = /\b(?:according to|per |reported by|cited in|source:|via |study|survey|benchmark|measured|documented in|states that|says that)\b/i;

  var LIMIT_MARKERS = /\b(?:limitation|limitations|caveat|caveats|does not (?:apply|cover|work)|doesn't (?:apply|cover|work)|not applicable|we did not|i did not|we have not|i have not|untested|out of scope|this (?:is|will) not|exception|when (?:this|it) (?:is|does not)|fails when|breaks when|only if|assumes|assumption|no evidence|could not (?:verify|confirm)|unverified|not verified|trade-?off)\b/i;

  var DATE_PATTERNS = [
    /\b(?:19|20)\d{2}-\d{2}-\d{2}\b/,
    /\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}\b/i,
    /\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:19|20)\d{2}\b/i,
    /\b(?:updated|published|last reviewed|revised|as of|measured|tested)\b[^.\n]{0,40}\b(?:19|20)\d{2}\b/i
  ];

  var TIME_SENSITIVE = /\b(?:currently|right now|at the moment|these days|today|nowadays|latest|newest|most recent|as it stands|at present|recently|now)\b/i;

  /* A quantity is interpretable when the number is followed by what it counts,
   * or carries a unit or currency. Word alternatives are boundary-anchored so
   * that "ms" does not match inside "problems". */
  var UNIT_SYMBOL = /(?:%|\$|\u00a3|\u20ac)/;
  var UNIT_WORD = /\b(?:percent|ms|milliseconds?|seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?|bytes?|kb|mb|gb|tb|px|rem|em|USD|EUR|GBP)\b/i;
  var NUMBER_WITH_TRAILING_NOUN = /\d(?:[\d,.]*\d)?\s*(?:%|\$|\u00a3|\u20ac)?\s*[a-z][a-z-]{1,}/i;
  var DANGLING_NUMBER = /(?:\bby\s+|\bto\s+|\bof\s+|\bfrom\s+)?\d(?:[\d,.]*\d)?\s*(?:[.,;:)\]]|$)/;

  function unique(values) {
    var seen = Object.create(null);
    var out = [];
    values.forEach(function (value) {
      if (!seen[value]) {
        seen[value] = true;
        out.push(value);
      }
    });
    return out;
  }

  function stripTags(html) {
    return html
      .replace(/<script\b[\s\S]*?<\/script>/gi, " ")
      .replace(/<style\b[\s\S]*?<\/style>/gi, " ")
      .replace(/<!--[\s\S]*?-->/g, " ")
      .replace(/<[^>]+>/g, " ");
  }

  function decodeEntities(value) {
    var named = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", mdash: "—", ndash: "–", rsquo: "’", lsquo: "‘", ldquo: "“", rdquo: "”", hellip: "…" };
    return String(value).replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, function (match, key) {
      var lower = key.toLowerCase();
      if (lower.charAt(0) === "#") {
        var hex = lower.charAt(1) === "x";
        var code = parseInt(lower.slice(hex ? 2 : 1), hex ? 16 : 10);
        return isFinite(code) ? String.fromCharCode(code) : match;
      }
      return named[lower] || match;
    });
  }

  function collapse(value) {
    return decodeEntities(value).replace(/\s+/g, " ").trim();
  }

  function looksLikeHtml(text) {
    return /<\s*(?:html|head|body|div|p|h1|h2|h3|section|article|main|span|script|meta)\b/i.test(text.slice(0, 4000));
  }

  /* Splits on sentence-final punctuation followed by a capital or digit. Uses a
   * lookbehind-free regex split rather than an in-band sentinel, so the source
   * file stays plain text. Abbreviations occasionally split early, which is
   * acceptable because every consumer of this is labelled heuristic. */
  function splitSentences(text) {
    if (!text) return [];
    return text
      .split(/(?<=[.!?])\s+(?=[A-Z0-9"'“])/)
      .map(function (part) { return part.trim(); })
      .filter(Boolean);
  }

  /* ---------------------------------------------------------------------- */
  /* Parsing                                                                */
  /* ---------------------------------------------------------------------- */

  /* Isolates the page's own content before anything is measured. Without this,
   * navigation, the footer, and a "Latest posts" list are read as page prose and
   * every check is polluted: verified on this site's own built article pages,
   * 2026-08-17, where the footer's "Latest posts" heading registered as an
   * undated time-relative claim.
   *
   * Preference order follows what the HTML actually declares, rather than
   * guessing at class names: <main>, then [role=main], then <article>, then the
   * whole body. Chrome elements are stripped in every case. */
  function extractMainRegion(input) {
    var candidates = [
      /<main\b[^>]*>([\s\S]*?)<\/main>/i,
      /<[a-z]+\b[^>]*role\s*=\s*["']main["'][^>]*>([\s\S]*?)<\/[a-z]+>/i,
      /<article\b[^>]*>([\s\S]*?)<\/article>/i,
      /<body\b[^>]*>([\s\S]*?)<\/body>/i
    ];
    var region = input;
    for (var i = 0; i < candidates.length; i += 1) {
      var found = candidates[i].exec(input);
      if (found && found[1] && found[1].replace(/<[^>]+>/g, "").trim().length > 200) {
        region = found[1];
        break;
      }
    }
    return region
      .replace(/<nav\b[\s\S]*?<\/nav>/gi, " ")
      .replace(/<footer\b[\s\S]*?<\/footer>/gi, " ")
      .replace(/<aside\b[\s\S]*?<\/aside>/gi, " ")
      .replace(/<form\b[\s\S]*?<\/form>/gi, " ");
  }

  function parseHtml(fullInput) {
    /* Head-level directives and JSON-LD are read from the whole document; prose
     * is read only from the content region. */
    var input = extractMainRegion(fullInput);
    var blocks = [];
    var headingPattern = /<h([1-6])\b[^>]*>([\s\S]*?)<\/h\1>/gi;
    var match;
    var marks = [];
    while ((match = headingPattern.exec(input))) {
      marks.push({ index: match.index, end: headingPattern.lastIndex, level: Number(match[1]), text: collapse(stripTags(match[2])) });
    }

    var cursor = 0;
    function pushProse(chunk) {
      var text = collapse(stripTags(chunk));
      if (text) blocks.push({ type: "paragraph", text: text });
    }
    marks.forEach(function (mark) {
      pushProse(input.slice(cursor, mark.index));
      blocks.push({ type: "heading", level: mark.level, text: mark.text });
      cursor = mark.end;
    });
    pushProse(input.slice(cursor));

    var jsonLdTypes = [];
    var jsonLdBlocks = fullInput.match(/<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi) || [];
    jsonLdBlocks.forEach(function (block) {
      var body = block.replace(/^[\s\S]*?>/, "").replace(/<\/script>\s*$/i, "");
      var types = body.match(/"@type"\s*:\s*(?:"([^"]+)"|\[([^\]]*)\])/g) || [];
      types.forEach(function (entry) {
        var single = /"@type"\s*:\s*"([^"]+)"/.exec(entry);
        if (single) return jsonLdTypes.push(single[1]);
        var many = /"@type"\s*:\s*\[([^\]]*)\]/.exec(entry);
        if (many) {
          (many[1].match(/"([^"]+)"/g) || []).forEach(function (quoted) {
            jsonLdTypes.push(quoted.replace(/"/g, ""));
          });
        }
      });
    });

    var robots = "";
    var robotsTag = /<meta\b[^>]*name\s*=\s*["']robots["'][^>]*>/i.exec(fullInput);
    if (robotsTag) {
      var content = /content\s*=\s*["']([^"']*)["']/i.exec(robotsTag[0]);
      robots = content ? content[1].toLowerCase() : "";
    }

    return {
      blocks: blocks,
      isHtml: true,
      jsonLdTypes: unique(jsonLdTypes),
      jsonLdCount: jsonLdBlocks.length,
      robots: robots,
      hasTimeElement: /<time\b/i.test(fullInput),
      dataNosnippetCount: (fullInput.match(/data-nosnippet/gi) || []).length,
      raw: input,
      fullRaw: fullInput
    };
  }

  function parseMarkdown(input) {
    var lines = input.split(/\r\n|\n|\r/);
    var blocks = [];
    var buffer = [];
    var inFence = false;

    function flush() {
      if (!buffer.length) return;
      var text = collapse(buffer.join(" "));
      if (text) blocks.push({ type: "paragraph", text: text });
      buffer = [];
    }

    lines.forEach(function (line) {
      if (/^\s*(?:```|~~~)/.test(line)) {
        flush();
        inFence = !inFence;
        return;
      }
      if (inFence) return;
      var heading = /^(#{1,6})\s+(.*)$/.exec(line);
      if (heading) {
        flush();
        blocks.push({ type: "heading", level: heading[1].length, text: collapse(heading[2].replace(/\s*#+\s*$/, "")) });
        return;
      }
      if (line.trim() === "") {
        flush();
        return;
      }
      buffer.push(line.replace(/^\s*(?:[-*+]|\d+[.)])\s+/, ""));
    });
    flush();

    return {
      blocks: blocks,
      isHtml: false,
      jsonLdTypes: [],
      jsonLdCount: 0,
      robots: "",
      hasTimeElement: false,
      dataNosnippetCount: 0,
      raw: input
    };
  }

  function parse(input) {
    return looksLikeHtml(input) ? parseHtml(input) : parseMarkdown(input);
  }

  /* ---------------------------------------------------------------------- */
  /* Checks                                                                 */
  /* ---------------------------------------------------------------------- */

  function makeCheck(id, title, status, confidence, basis, detail, evidence) {
    return {
      id: id,
      title: title,
      status: status,
      confidence: confidence,
      basis: basis,
      detail: detail,
      evidence: evidence || []
    };
  }

  function firstProse(doc) {
    for (var i = 0; i < doc.blocks.length; i += 1) {
      if (doc.blocks[i].type === "paragraph" && doc.blocks[i].text.length > 40) return doc.blocks[i];
    }
    for (var j = 0; j < doc.blocks.length; j += 1) {
      if (doc.blocks[j].type === "paragraph") return doc.blocks[j];
    }
    return null;
  }

  function checkDirectAnswerFirst(doc) {
    var basis = "[NNG-IP] NN/g, 2018-02-11: the most important information, or the conclusion, is presented first. [G-AIO], 2026-07-10, on organising content clearly.";
    var block = firstProse(doc);
    if (!block) {
      return makeCheck("direct-answer-first", "A direct answer opens the page", SKIPPED, HEURISTIC, basis,
        "No prose was found to examine.", []);
    }
    var sentences = splitSentences(block.text);
    var opening = sentences.slice(0, 2).join(" ");
    var hits = [];
    PREAMBLE_PATTERNS.forEach(function (pattern) {
      var found = pattern.exec(opening);
      if (found) hits.push(found[0]);
    });
    if (hits.length) {
      return makeCheck("direct-answer-first", "A direct answer opens the page", ATTENTION, HEURISTIC, basis,
        "The opening establishes a topic before answering it. An engine lifting the first passage would quote scene-setting rather than an answer.",
        unique(hits).map(function (hit) { return { excerpt: hit }; }));
    }
    if (opening.length < 40) {
      return makeCheck("direct-answer-first", "A direct answer opens the page", ATTENTION, HEURISTIC, basis,
        "The opening is too short to contain an answer.", [{ excerpt: opening }]);
    }
    return makeCheck("direct-answer-first", "A direct answer opens the page", PASS, HEURISTIC, basis,
      "The opening asserts something rather than introducing a topic.", [{ excerpt: sentences[0] || opening }]);
  }

  function isTopicLabel(text) {
    var normalised = text.toLowerCase().replace(/[^a-z0-9'\s]/g, "").replace(/\s+/g, " ").trim();
    if (!normalised) return true;
    if (TOPIC_LABEL_WORDS.indexOf(normalised) !== -1) return true;
    if (/\?$/.test(text.trim())) return false;
    var words = normalised.split(" ");
    if (words.length <= 2 && !VERB_HINT.test(normalised)) return true;
    if (!VERB_HINT.test(normalised) && words.length <= 4) return true;
    return false;
  }

  function checkHeadingsCarryClaims(doc) {
    var basis = "[NNG-LC] NN/g, 2019-08-25: the layer-cake pattern, where a reader fixates on headings alone, is \"by far the most effective way in which users can scan pages\", and the F-pattern happens \"in the absence of subheadings\". A heading a reader sees in isolation has to carry the point.";
    var headings = doc.blocks.filter(function (block) { return block.type === "heading" && block.level >= 2; });
    if (!headings.length) {
      return makeCheck("headings-carry-claims", "Headings ask or assert, rather than label", ATTENTION, HEURISTIC, basis,
        "No H2 or lower headings were found. With no subheadings a scanning reader falls back to the F-pattern and reads almost nothing.", []);
    }
    var labels = headings.filter(function (heading) { return isTopicLabel(heading.text); });
    if (labels.length) {
      return makeCheck("headings-carry-claims", "Headings ask or assert, rather than label", ATTENTION, HEURISTIC, basis,
        labels.length + " of " + headings.length + " headings name a topic without asking a question or stating a conclusion.",
        labels.slice(0, 8).map(function (heading) { return { excerpt: heading.text }; }));
    }
    return makeCheck("headings-carry-claims", "Headings ask or assert, rather than label", PASS, HEURISTIC, basis,
      "All " + headings.length + " subheadings state or ask something.", []);
  }

  function checkSelfContainedPassages(doc) {
    var basis = "[G-AIO] 2026-07-10 states a page must be \"eligible to be shown in Google Search with a snippet\". A snippet is a passage, so a passage that depends on the sentence before it cannot be lifted intact.";
    var offenders = [];
    var examined = 0;
    for (var i = 0; i < doc.blocks.length; i += 1) {
      if (doc.blocks[i].type !== "heading") continue;
      for (var j = i + 1; j < doc.blocks.length; j += 1) {
        if (doc.blocks[j].type === "heading") break;
        if (doc.blocks[j].type !== "paragraph") continue;
        examined += 1;
        var sentence = splitSentences(doc.blocks[j].text)[0] || "";
        if (PRONOUN_OPENERS.test(sentence)) offenders.push({ excerpt: sentence.slice(0, 160) });
        break;
      }
    }
    if (!examined) {
      return makeCheck("self-contained-passages", "Each section opens by naming its subject", SKIPPED, HEURISTIC, basis,
        "No section bodies were found to examine.", []);
    }
    if (offenders.length) {
      return makeCheck("self-contained-passages", "Each section opens by naming its subject", ATTENTION, HEURISTIC, basis,
        offenders.length + " of " + examined + " sections open with a pronoun or demonstrative instead of naming the subject.",
        offenders.slice(0, 6));
    }
    return makeCheck("self-contained-passages", "Each section opens by naming its subject", PASS, HEURISTIC, basis,
      "All " + examined + " section openings name their subject.", []);
  }

  function numericSentences(doc) {
    var found = [];
    doc.blocks.forEach(function (block) {
      if (block.type !== "paragraph") return;
      splitSentences(block.text).forEach(function (sentence) {
        if (/\d/.test(sentence) && !/^\s*\d+[.)]\s/.test(sentence)) found.push(sentence);
      });
    });
    return found;
  }

  function checkQuantitiesCarryUnits(doc) {
    var basis = "[G-HC] 2025-12-10 asks whether content provides \"original information, reporting, research, or analysis\". A quantity an engine cannot interpret carries none of that, because the number stops meaning anything once the surrounding page is gone.";
    var sentences = numericSentences(doc);
    if (!sentences.length) {
      return makeCheck("quantities-carry-units", "Numbers say what they count", SKIPPED, HEURISTIC, basis,
        "No numeric claims were found.", []);
    }
    var bare = sentences.filter(function (sentence) {
      if (/\b(?:19|20)\d{2}\b/.test(sentence)) return false;
      if (/\bv?\d+\.\d+/.test(sentence)) return false;
      if (UNIT_SYMBOL.test(sentence) || UNIT_WORD.test(sentence)) return false;
      if (NUMBER_WITH_TRAILING_NOUN.test(sentence)) return false;
      return DANGLING_NUMBER.test(sentence);
    });
    if (bare.length) {
      return makeCheck("quantities-carry-units", "Numbers say what they count", ATTENTION, HEURISTIC, basis,
        bare.length + " of " + sentences.length + " numeric sentences leave a number without a unit, currency, period, or the noun it counts. This check is a text pattern and will misread some valid sentences.",
        bare.slice(0, 6).map(function (sentence) { return { excerpt: sentence.slice(0, 160) }; }));
    }
    return makeCheck("quantities-carry-units", "Numbers say what they count", PASS, HEURISTIC, basis,
      "All " + sentences.length + " numeric sentences say what the number refers to.", []);
  }

  function checkClaimsCarrySources(doc) {
    var basis = "[QRG] 2025-09-10 names \"Lacks adequate effort and first-hand experience from the content creator\" a Low-quality criterion, illustrated by content paraphrased from other sources. [G-HC] 2025-12-10 asks for original information, reporting, research, or analysis.";
    var sentences = numericSentences(doc);
    if (!sentences.length) {
      return makeCheck("claims-carry-sources", "Quantified claims name a source", SKIPPED, HEURISTIC, basis,
        "No quantified claims were found.", []);
    }
    var linkish = doc.isHtml
      ? (doc.raw.match(/<a\b[^>]*href/gi) || []).length
      : (doc.raw.match(/\]\(https?:\/\//g) || []).length + (doc.raw.match(/https?:\/\//g) || []).length;
    var unsourced = sentences.filter(function (sentence) {
      return !HEDGE_SOURCE_MARKERS.test(sentence) && !/https?:\/\//.test(sentence);
    });
    if (unsourced.length === sentences.length && linkish === 0) {
      return makeCheck("claims-carry-sources", "Quantified claims name a source", ATTENTION, HEURISTIC, basis,
        "The page makes " + sentences.length + " quantified claims and contains no links or attribution language at all.",
        unsourced.slice(0, 5).map(function (sentence) { return { excerpt: sentence.slice(0, 160) }; }));
    }
    if (unsourced.length > sentences.length / 2) {
      return makeCheck("claims-carry-sources", "Quantified claims name a source", ATTENTION, HEURISTIC, basis,
        unsourced.length + " of " + sentences.length + " quantified claims sit near no source or attribution. Attribution elsewhere on the page does not travel with a lifted passage.",
        unsourced.slice(0, 5).map(function (sentence) { return { excerpt: sentence.slice(0, 160) }; }));
    }
    return makeCheck("claims-carry-sources", "Quantified claims name a source", PASS, HEURISTIC, basis,
      "Most quantified claims sit near attribution or a link.", []);
  }

  function checkDatedEvidence(doc) {
    var basis = "[OBS] 2026-08-17: the low-authority page Google cited in its AI Overview for `docs as code` carried both a publish date and a visible revision date two days later. An undated claim also gives a retrieval system nothing to judge freshness by.";
    var haystack = doc.fullRaw || doc.raw;
    var hasDate = DATE_PATTERNS.some(function (pattern) { return pattern.test(haystack); }) || doc.hasTimeElement;
    var timeSensitive = [];
    doc.blocks.forEach(function (block) {
      if (block.type !== "paragraph") return;
      splitSentences(block.text).forEach(function (sentence) {
        if (TIME_SENSITIVE.test(sentence) && !DATE_PATTERNS.some(function (p) { return p.test(sentence); })) {
          timeSensitive.push(sentence);
        }
      });
    });

    if (!hasDate) {
      return makeCheck("dated-evidence", "The page and its claims are dated", ATTENTION, HEURISTIC, basis,
        "No date was found anywhere on the page." + (timeSensitive.length ? " It also makes " + timeSensitive.length + " time-relative claims." : ""),
        timeSensitive.slice(0, 4).map(function (s) { return { excerpt: s.slice(0, 160) }; }));
    }
    if (timeSensitive.length) {
      return makeCheck("dated-evidence", "The page and its claims are dated", ATTENTION, HEURISTIC, basis,
        "The page carries a date, but " + timeSensitive.length + " claims are time-relative without one in the same sentence. Lifted alone, those claims lose their reference point.",
        timeSensitive.slice(0, 6).map(function (s) { return { excerpt: s.slice(0, 160) }; }));
    }
    return makeCheck("dated-evidence", "The page and its claims are dated", PASS, HEURISTIC, basis,
      "A date is present and no time-relative claim is left undated.", []);
  }

  function checkLiftableDefinition(doc) {
    var basis = "[OBS] 2026-08-17: SERP pulls for definitional queries in this niche returned AI Overviews assembled from short definitional passages. A clean \"X is Y\" sentence is the unit such an answer is built from.";
    var candidates = [];
    var budget = 0;
    for (var i = 0; i < doc.blocks.length && budget < 12; i += 1) {
      if (doc.blocks[i].type !== "paragraph") continue;
      budget += 1;
      var sentences = splitSentences(doc.blocks[i].text);
      for (var j = 0; j < sentences.length; j += 1) {
        var sentence = sentences[j];
        if (!/^[A-Z][^.!?]{2,80}?\s+(?:is|are)\s+(?:a|an|the|not|two|the practice|the process)?\b/.test(sentence)) continue;
        if (sentence.length < 30 || sentence.length > 320) continue;
        if (PRONOUN_OPENERS.test(sentence)) continue;
        candidates.push(sentence);
      }
    }
    if (!candidates.length) {
      return makeCheck("liftable-definition", "A definition can be lifted cleanly", ATTENTION, HEURISTIC, basis,
        "No self-contained definitional sentence was found near the top of the page. Pages answering \"what is X\" queries need one that survives being quoted alone.", []);
    }
    return makeCheck("liftable-definition", "A definition can be lifted cleanly", PASS, HEURISTIC, basis,
      "A definitional sentence is available for extraction.",
      candidates.slice(0, 2).map(function (sentence) { return { excerpt: sentence.slice(0, 200) }; }));
  }

  function checkStatesItsLimits(doc) {
    var basis = "[QRG] 2025-09-10 makes Trust the most important E-E-A-T component. [OBS] 2026-08-17: the AI-Overview-cited page devoted a section to answering eight specific objections, which is also what produced its most quotable passages.";
    var hits = [];
    doc.blocks.forEach(function (block) {
      if (block.type !== "paragraph") return;
      splitSentences(block.text).forEach(function (sentence) {
        if (LIMIT_MARKERS.test(sentence)) hits.push(sentence);
      });
    });
    if (!hits.length) {
      return makeCheck("states-its-limits", "The page states where it does not apply", ATTENTION, HEURISTIC, basis,
        "No limitation, caveat, exception, or trade-off was found. A page that claims to work everywhere reads as unqualified rather than confident.", []);
    }
    return makeCheck("states-its-limits", "The page states where it does not apply", PASS, HEURISTIC, basis,
      hits.length + " passages name a limit, exception, or trade-off.",
      hits.slice(0, 3).map(function (sentence) { return { excerpt: sentence.slice(0, 160) }; }));
  }

  /* Snippet eligibility is the one hard gate in this whole tool, and it is the
   * only check that restates a requirement rather than a correlation. */
  function checkSnippetEligibility(doc) {
    var basis = "[G-AIO] 2026-07-10, verbatim: \"To be eligible to be shown in generative AI features on Google Search, a page must be indexed and eligible to be shown in Google Search with a snippet, fulfilling the Search technical requirements.\"";
    if (!doc.isHtml && !doc.robots) {
      return makeCheck("snippet-eligibility", "Snippets are not blocked", SKIPPED, DOCUMENTED, basis,
        "This check needs the page's HTML. Use the URL mode, or paste the full HTML source rather than the text.", []);
    }
    var problems = [];
    if (/\bnoindex\b/.test(doc.robots)) problems.push({ excerpt: "meta robots: " + doc.robots, note: "noindex" });
    if (/\bnosnippet\b/.test(doc.robots)) problems.push({ excerpt: "meta robots: " + doc.robots, note: "nosnippet" });
    var maxSnippet = /max-snippet\s*:\s*(-?\d+)/.exec(doc.robots);
    if (maxSnippet && Number(maxSnippet[1]) >= 0) {
      problems.push({ excerpt: "meta robots: max-snippet:" + maxSnippet[1], note: "max-snippet" });
    }
    if (problems.length) {
      return makeCheck("snippet-eligibility", "Snippets are not blocked", ATTENTION, DOCUMENTED, basis,
        "The page restricts snippets, which by Google's own wording makes it ineligible for AI Overviews and AI Mode. This is the one finding here that is a stated requirement rather than a heuristic.",
        problems);
    }
    var detail = "No noindex, nosnippet, or restrictive max-snippet was found.";
    if (doc.dataNosnippetCount) {
      detail += " " + doc.dataNosnippetCount + " data-nosnippet attributes exclude specific passages, which is a deliberate choice worth confirming.";
    }
    return makeCheck("snippet-eligibility", "Snippets are not blocked", PASS, DOCUMENTED, basis, detail, []);
  }

  /* Reported as information, never as a requirement, because Google says plainly
   * that it is not one. */
  function checkSchema(doc) {
    var basis = "[G-AIO] 2026-07-10, verbatim: \"Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add.\" It is reported here for rich-result eligibility only.";
    if (!doc.isHtml) {
      return makeCheck("schema-present", "Structured data, for rich results only", SKIPPED, DOCUMENTED, basis,
        "This check needs the page's HTML.", []);
    }
    if (!doc.jsonLdCount) {
      return makeCheck("schema-present", "Structured data, for rich results only", INFO, DOCUMENTED, basis,
        "No JSON-LD found. This does not affect AI Overview eligibility. Adding schema for that reason is not supported by Google's guidance.", []);
    }
    return makeCheck("schema-present", "Structured data, for rich results only", INFO, DOCUMENTED, basis,
      doc.jsonLdCount + " JSON-LD block(s) found. Useful for rich results, and not an AI Overview factor.",
      doc.jsonLdTypes.slice(0, 8).map(function (type) { return { excerpt: type }; }));
  }

  /* ---------------------------------------------------------------------- */
  /* Entry point                                                            */
  /* ---------------------------------------------------------------------- */

  function check(input, options) {
    var text = typeof input === "string" ? input : "";
    var settings = options || {};
    if (text.trim() === "") {
      return {
        checks: [],
        summary: {
          passed: 0, attention: 0, info: 0, skipped: 0, applicable: 0,
          band: "none", bandLabel: "nothing to check", grade: "f",
          isHtml: false, blocks: 0, headings: 0, words: 0
        }
      };
    }

    var doc = parse(text);
    /* A page can be excluded by the X-Robots-Tag response header alone, with
     * nothing visible in its markup, so the header is merged into the robots
     * directives before the snippet check reads them. */
    if (settings.xRobotsTag) {
      doc.robots = (doc.robots ? doc.robots + ", " : "") + String(settings.xRobotsTag).toLowerCase();
      doc.robotsFromHeader = true;
    }
    var checks = [
      checkSnippetEligibility(doc),
      checkDirectAnswerFirst(doc),
      checkHeadingsCarryClaims(doc),
      checkSelfContainedPassages(doc),
      checkLiftableDefinition(doc),
      checkDatedEvidence(doc),
      checkClaimsCarrySources(doc),
      checkQuantitiesCarryUnits(doc),
      checkStatesItsLimits(doc),
      checkSchema(doc)
    ];

    var passed = 0;
    var attention = 0;
    var info = 0;
    var skipped = 0;
    checks.forEach(function (item) {
      if (item.status === PASS) passed += 1;
      else if (item.status === ATTENTION) attention += 1;
      else if (item.status === INFO) info += 1;
      else skipped += 1;
    });
    var applicable = passed + attention;

    /* A count, not a score. Bands are coarse on purpose: there is no published
     * calibration that would justify a weighted number, so inventing one would
     * imply precision this tool does not have. */
    var band = "review";
    var bandLabel = "several checks need attention";
    var grade = "d";
    if (!applicable) {
      band = "none";
      bandLabel = "nothing applicable to check";
      grade = "f";
    } else if (attention === 0) {
      band = "clean";
      bandLabel = "every applicable check passed";
      grade = "a";
    } else if (attention === 1) {
      band = "close";
      bandLabel = "one check needs attention";
      grade = "b";
    } else if (attention <= 3) {
      band = "mixed";
      bandLabel = attention + " checks need attention";
      grade = "c";
    } else if (attention <= 5) {
      band = "review";
      bandLabel = attention + " checks need attention";
      grade = "d";
    } else {
      band = "weak";
      bandLabel = attention + " checks need attention";
      grade = "f";
    }

    var words = doc.blocks.reduce(function (total, block) {
      return total + (block.text ? block.text.split(/\s+/).length : 0);
    }, 0);

    return {
      checks: checks,
      summary: {
        passed: passed,
        attention: attention,
        info: info,
        skipped: skipped,
        applicable: applicable,
        band: band,
        bandLabel: bandLabel,
        grade: grade,
        isHtml: doc.isHtml,
        blocks: doc.blocks.length,
        headings: doc.blocks.filter(function (b) { return b.type === "heading"; }).length,
        words: words
      }
    };
  }

  return {
    check: check,
    parse: parse,
    STATUS: { PASS: PASS, ATTENTION: ATTENTION, INFO: INFO, SKIPPED: SKIPPED },
    CONFIDENCE: { DOCUMENTED: DOCUMENTED, HEURISTIC: HEURISTIC }
  };
});
