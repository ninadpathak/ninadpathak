/*
 * AI crawler access checker — rule engine.
 *
 * Pure functions only. No DOM, no network, no globals beyond the export, so the
 * browser and tests/test_robots_access.py (through node) run the same code.
 *
 * THE QUESTION THIS ANSWERS
 *
 * Every AI platform splits its crawlers by purpose. One agent decides whether the
 * platform may cite a page in an answer; a different agent decides whether the
 * page may be used to train a model. Blocking the wrong one silently removes a
 * site from AI answers, and blocking the right one is a legitimate choice that
 * looks alarming to anyone auditing the file casually.
 *
 * Reading a list of user agents does not tell anyone what their own robots.txt
 * does, because robots.txt group selection is genuinely counter-intuitive: only
 * the single most specific matching user-agent group applies, and the other
 * matching groups are ignored entirely (RFC 9309 §2.2.1). That is the gap this
 * tool fills.
 *
 * WHAT IT DOES NOT CLAIM
 *
 * robots.txt is not the whole story. A WAF or CDN can block a crawler at the
 * edge regardless of what the file says, and a crawler can ignore the file. The
 * tool reports what the file permits, which is a different statement from what
 * actually reaches the site, and it says so rather than implying certainty.
 *
 * Matching follows RFC 9309 (Robots Exclusion Protocol, published 2022-09):
 *   - User-agent matching is case-insensitive and matches a product token.
 *   - Only the most specific matching group applies; if none matches, "*" does.
 *   - Within a group the longest matching rule wins; on equal length, Allow wins.
 *   - An empty Disallow value permits everything.
 *   - "*" matches any sequence and "$" anchors the end of a path.
 *
 * Agent facts are sourced individually in AGENTS below, each with the document
 * and the date it was read.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.RobotsAccessCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var CITE = "cite";
  var TRAIN = "train";
  var USER = "user";

  /*
   * Purpose is what makes this tool useful, so it is recorded per agent rather
   * than inferred from the name. Every `source` was read on 2026-08-17.
   */
  var AGENTS = [
    {
      platform: "ChatGPT",
      token: "OAI-SearchBot",
      purpose: CITE,
      note: "Surfaces websites in ChatGPT's search features. Sites blocking it \"will not be shown in ChatGPT search answers, though can still appear as navigational links.\"",
      source: "developers.openai.com/api/docs/bots, read 2026-08-17"
    },
    {
      platform: "ChatGPT",
      token: "ChatGPT-User",
      purpose: USER,
      note: "Fetches a page when a person asks ChatGPT or a custom GPT a question that needs it.",
      source: "developers.openai.com/api/docs/bots, read 2026-08-17"
    },
    {
      platform: "ChatGPT",
      token: "GPTBot",
      purpose: TRAIN,
      note: "Crawls content that may be used to train OpenAI's foundation models. Blocking it does not affect citation.",
      source: "developers.openai.com/api/docs/bots, read 2026-08-17"
    },
    {
      platform: "Claude",
      token: "Claude-SearchBot",
      purpose: CITE,
      note: "Navigates the web to improve search result quality for Claude users.",
      source: "support.claude.com article 8896518, read 2026-08-17"
    },
    {
      platform: "Claude",
      token: "Claude-User",
      purpose: USER,
      note: "Fetches a page when a person asks Claude a question that needs it.",
      source: "support.claude.com article 8896518, read 2026-08-17"
    },
    {
      platform: "Claude",
      token: "ClaudeBot",
      purpose: TRAIN,
      note: "Collects web content that may contribute to training. Anthropic states that blocking it leaves Claude-SearchBot and Claude-User unaffected.",
      source: "support.claude.com article 8896518, read 2026-08-17"
    },
    {
      platform: "Perplexity",
      token: "PerplexityBot",
      purpose: CITE,
      note: "Surfaces and links websites in Perplexity results. Perplexity states it is not used to crawl content for foundation models.",
      source: "docs.perplexity.ai/guides/bots, read 2026-08-17"
    },
    {
      platform: "Perplexity",
      token: "Perplexity-User",
      purpose: USER,
      note: "Visits a page to answer a specific user question, and links it in the response.",
      source: "docs.perplexity.ai/guides/bots, read 2026-08-17"
    },
    {
      platform: "Google Search, AI Overviews and AI Mode",
      token: "Googlebot",
      purpose: CITE,
      note: "AI Overviews and AI Mode are part of Search and use Googlebot. There is no separate agent to allow for them.",
      source: "developers.google.com/search/docs/crawling-indexing, read 2026-08-17"
    },
    {
      platform: "Gemini apps and Vertex AI grounding",
      token: "Google-Extended",
      purpose: TRAIN,
      note: "Controls Gemini apps and Vertex AI grounding and model improvement. It does not affect Google Search, AI Overviews, or AI Mode.",
      source: "Google crawler documentation, read 2026-08-17"
    },
    {
      platform: "Bing and Copilot",
      token: "Bingbot",
      purpose: CITE,
      note: "Microsoft's search crawler. Copilot answers draw on the Bing index.",
      source: "Bing webmaster documentation, read 2026-08-17"
    },
    {
      platform: "Apple",
      token: "Applebot",
      purpose: CITE,
      note: "Powers Siri and Spotlight suggestions.",
      source: "Apple support documentation, read 2026-08-17"
    },
    {
      platform: "Apple Intelligence",
      token: "Applebot-Extended",
      purpose: TRAIN,
      note: "A training opt-out only. Blocking it does not remove a site from Apple search features.",
      source: "Apple support documentation, read 2026-08-17"
    },
    {
      platform: "Common Crawl",
      token: "CCBot",
      purpose: TRAIN,
      note: "Builds the Common Crawl corpus, which many model builders train on. Not a citation agent for any assistant.",
      source: "commoncrawl.org, read 2026-08-17"
    },
    {
      platform: "Meta AI",
      token: "meta-externalagent",
      purpose: TRAIN,
      note: "Collects content for Meta's AI training.",
      source: "Meta developer documentation, read 2026-08-17"
    },
    {
      platform: "ByteDance",
      token: "Bytespider",
      purpose: TRAIN,
      note: "ByteDance's crawler, widely reported as a training crawler.",
      source: "Widely documented crawler behaviour, read 2026-08-17"
    },
    {
      platform: "Amazon",
      token: "Amazonbot",
      purpose: CITE,
      note: "Amazon's crawler, used for Alexa answers and search features.",
      source: "Amazon developer documentation, read 2026-08-17"
    }
  ];

  function normaliseLine(line) {
    var withoutComment = line.replace(/#.*$/, "");
    return withoutComment.trim();
  }

  /*
   * Parses robots.txt into groups. Consecutive User-agent lines share one group,
   * per RFC 9309: a rule following several agent lines applies to all of them.
   */
  function parse(text) {
    var lines = String(text == null ? "" : text).split(/\r\n|\n|\r/);
    var groups = [];
    var current = null;
    var expectingAgents = false;
    var sitemaps = [];
    var contentSignals = [];
    var unknownFields = [];

    lines.forEach(function (raw, index) {
      var line = normaliseLine(raw);
      if (line === "") return;

      var split = line.indexOf(":");
      if (split === -1) {
        unknownFields.push({ line: index + 1, text: line });
        return;
      }
      var field = line.slice(0, split).trim().toLowerCase();
      var value = line.slice(split + 1).trim();

      if (field === "user-agent") {
        if (!expectingAgents || !current) {
          current = { agents: [], rules: [], crawlDelay: null, line: index + 1 };
          groups.push(current);
          expectingAgents = true;
        }
        current.agents.push(value.toLowerCase());
        return;
      }

      if (field === "sitemap") {
        sitemaps.push({ line: index + 1, value: value });
        return;
      }

      if (field === "content-signal") {
        contentSignals.push({ line: index + 1, value: value, group: current });
        return;
      }

      expectingAgents = false;

      if (field === "allow" || field === "disallow") {
        if (!current) {
          // Rules before any User-agent line belong to no group and are ignored
          // by conforming parsers. Recorded so the report can say so.
          unknownFields.push({ line: index + 1, text: line, orphanRule: true });
          return;
        }
        current.rules.push({ type: field, path: value, line: index + 1 });
        return;
      }

      if (field === "crawl-delay") {
        if (current) current.crawlDelay = value;
        return;
      }

      unknownFields.push({ line: index + 1, text: line });
    });

    return {
      groups: groups,
      sitemaps: sitemaps,
      contentSignals: contentSignals,
      unknownFields: unknownFields,
      lineCount: lines.length
    };
  }

  /* RFC 9309 group selection: the single most specific matching group wins. A
   * literal token match beats "*", and among literal matches the longest wins.
   *
   * Groups sharing the same most-specific token are merged rather than having
   * the first one win, because the spec treats records with the same user-agent
   * value as one group. Real files rely on this: nytimes.com/robots.txt carried
   * two separate "User-agent: Googlebot" groups when read on 2026-08-17, and
   * honouring only the first would silently drop the second one's rules. */
  function mergeGroups(groups) {
    if (groups.length === 1) return groups[0];
    var merged = { agents: [], rules: [], crawlDelay: null, line: groups[0].line, mergedFrom: [] };
    groups.forEach(function (group) {
      merged.agents = merged.agents.concat(group.agents);
      merged.rules = merged.rules.concat(group.rules);
      if (merged.crawlDelay === null) merged.crawlDelay = group.crawlDelay;
      merged.mergedFrom.push(group.line);
    });
    return merged;
  }

  function selectGroup(parsed, token) {
    var lower = token.toLowerCase();
    var bestLength = -1;
    var bestGroups = [];
    var wildcardGroups = [];

    parsed.groups.forEach(function (group) {
      var groupBest = -1;
      var isWildcard = false;
      group.agents.forEach(function (agent) {
        if (agent === "*") {
          isWildcard = true;
          return;
        }
        // A robots.txt product token matches if it is a prefix of the crawler's
        // token, compared case-insensitively.
        if (lower.indexOf(agent) === 0 && agent.length > groupBest) groupBest = agent.length;
      });
      if (isWildcard) wildcardGroups.push(group);
      if (groupBest === -1) return;
      if (groupBest > bestLength) {
        bestLength = groupBest;
        bestGroups = [group];
      } else if (groupBest === bestLength) {
        bestGroups.push(group);
      }
    });

    if (bestGroups.length) {
      return { group: mergeGroups(bestGroups), matchedBy: "explicit", specificity: bestLength, groupCount: bestGroups.length };
    }
    if (wildcardGroups.length) {
      return { group: mergeGroups(wildcardGroups), matchedBy: "wildcard", specificity: 0, groupCount: wildcardGroups.length };
    }
    return { group: null, matchedBy: "none", specificity: -1, groupCount: 0 };
  }

  /* Converts a robots.txt path pattern into a regex honouring "*" and "$". */
  function patternToRegex(pattern) {
    var anchored = false;
    var body = pattern;
    if (/\$$/.test(body)) {
      anchored = true;
      body = body.slice(0, -1);
    }
    var escaped = body.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
    return new RegExp("^" + escaped + (anchored ? "$" : ""));
  }

  /*
   * RFC 9309 rule precedence: the longest matching rule wins, and Allow wins a
   * tie. An empty Disallow value permits everything and is not a match on path.
   */
  function evaluate(group, path) {
    if (!group) return { allowed: true, reason: "no-group", rule: null };

    var winner = null;
    var winnerLength = -1;

    group.rules.forEach(function (rule) {
      if (rule.type === "disallow" && rule.path === "") return;
      if (rule.path === "") {
        // "Allow:" with an empty value carries no path and is ignored.
        return;
      }
      var matches = false;
      try {
        matches = patternToRegex(rule.path).test(path);
      } catch (error) {
        matches = false;
      }
      if (!matches) return;
      var length = rule.path.replace(/\$$/, "").length;
      if (length > winnerLength || (length === winnerLength && rule.type === "allow")) {
        winner = rule;
        winnerLength = length;
      }
    });

    if (!winner) {
      var hasEmptyDisallow = group.rules.some(function (rule) {
        return rule.type === "disallow" && rule.path === "";
      });
      return {
        allowed: true,
        reason: hasEmptyDisallow ? "empty-disallow" : "no-matching-rule",
        rule: null
      };
    }
    return { allowed: winner.type === "allow", reason: "rule", rule: winner };
  }

  function check(text, options) {
    var settings = options || {};
    var path = settings.path || "/";
    var source = String(text == null ? "" : text);
    var parsed = parse(source);

    var fileIsEmpty = source.trim() === "";
    var hasAnyGroup = parsed.groups.length > 0;

    var results = AGENTS.map(function (agent) {
      var selection = selectGroup(parsed, agent.token);
      var verdict = evaluate(selection.group, path);

      var explanation;
      if (fileIsEmpty) {
        explanation = "No robots.txt rules were found, so nothing is disallowed. An absent or empty file permits everything.";
      } else if (selection.matchedBy === "explicit") {
        explanation = "Matched its own User-agent group. Under the protocol only the most specific matching group applies, so any \"*\" group is ignored for this crawler.";
      } else if (selection.matchedBy === "wildcard") {
        explanation = "Not named in the file, so it falls under the \"User-agent: *\" group.";
      } else {
        explanation = "Not named in the file, and there is no \"User-agent: *\" group, so nothing applies to it.";
      }

      if (verdict.reason === "rule") {
        explanation += " The governing rule is \"" + verdict.rule.type.charAt(0).toUpperCase() +
          verdict.rule.type.slice(1) + ": " + verdict.rule.path + "\" on line " + verdict.rule.line + ".";
      } else if (verdict.reason === "empty-disallow") {
        explanation += " Its group carries an empty Disallow, which permits everything.";
      } else if (verdict.reason === "no-matching-rule" && selection.group) {
        explanation += " No rule in that group matches this path.";
      }

      return {
        platform: agent.platform,
        token: agent.token,
        purpose: agent.purpose,
        allowed: verdict.allowed,
        matchedBy: selection.matchedBy,
        rulePath: verdict.rule ? verdict.rule.path : null,
        ruleType: verdict.rule ? verdict.rule.type : null,
        ruleLine: verdict.rule ? verdict.rule.line : null,
        note: agent.note,
        source: agent.source,
        explanation: explanation
      };
    });

    var citation = results.filter(function (item) { return item.purpose === CITE; });
    var training = results.filter(function (item) { return item.purpose === TRAIN; });
    var userAgents = results.filter(function (item) { return item.purpose === USER; });

    var citationBlocked = citation.filter(function (item) { return !item.allowed; });
    var trainingBlocked = training.filter(function (item) { return !item.allowed; });
    var userBlocked = userAgents.filter(function (item) { return !item.allowed; });

    /* A count, not a score. There is no correct number of allowed crawlers: a
     * training opt-out is a legitimate editorial choice, not a defect, so the
     * headline counts citation access only and reports training separately. */
    var posture = "mixed";
    var postureLabel = "";
    if (citationBlocked.length === 0 && trainingBlocked.length === 0) {
      posture = "open";
      postureLabel = "everything allowed";
    } else if (citationBlocked.length === 0 && trainingBlocked.length === training.length) {
      posture = "cite-only";
      postureLabel = "citation allowed, training opted out";
    } else if (citationBlocked.length === 0) {
      posture = "cite-only";
      postureLabel = "citation allowed, training partly opted out";
    } else if (citationBlocked.length === citation.length) {
      posture = "closed";
      postureLabel = "citation blocked everywhere";
    } else {
      posture = "mixed";
      postureLabel = citationBlocked.length + " of " + citation.length + " citation crawlers blocked";
    }

    var grade = "a";
    if (citationBlocked.length === 0) grade = "a";
    else if (citationBlocked.length === 1) grade = "c";
    else if (citationBlocked.length < citation.length) grade = "d";
    else grade = "f";

    var notes = [];

    if (!hasAnyGroup && !fileIsEmpty) {
      notes.push({
        id: "no-groups",
        severity: "warning",
        message: "No User-agent group was found, so no rule in this file applies to any crawler.",
        basis: "RFC 9309 §2.2.1: rules take effect only inside a group introduced by a User-agent line."
      });
    }

    parsed.unknownFields.forEach(function (field) {
      if (field.orphanRule) {
        notes.push({
          id: "rule-before-user-agent",
          severity: "warning",
          line: field.line,
          excerpt: field.text,
          message: "This rule appears before any User-agent line, so conforming crawlers ignore it.",
          basis: "RFC 9309 §2.2.1."
        });
      }
    });

    if (parsed.contentSignals.length) {
      var signalText = parsed.contentSignals.map(function (entry) { return entry.value; }).join("; ");
      var declaresAiInput = /\bai-input\s*=/.test(signalText);
      notes.push({
        id: "content-signal",
        severity: "info",
        excerpt: signalText,
        message: declaresAiInput
          ? "A Content-Signal header is present and declares ai-input, which is the signal covering retrieval for generative answers."
          : "A Content-Signal header is present but does not declare ai-input, the signal covering retrieval for generative answers. Per the convention, omitting a signal neither grants nor restricts permission, so the intent is unstated rather than permissive.",
        basis: "Content Signals is a Cloudflare-led convention, not an enforced standard, and is advisory either way."
      });
    }

    if (!parsed.sitemaps.length && !fileIsEmpty) {
      notes.push({
        id: "no-sitemap",
        severity: "info",
        message: "No Sitemap line. It is optional, and declaring one is the cheapest way to make a crawler's discovery job easier.",
        basis: "RFC 9309 lists Sitemap as a non-group field."
      });
    }

    notes.push({
      id: "edge-blocking",
      severity: "info",
      message: "This reads the file only. A CDN or WAF can block a crawler at the edge whatever the file says, and a crawler can ignore the file. Confirm at the edge before concluding a crawler has access.",
      basis: "Stated limitation of this tool, not a finding about your site."
    });

    return {
      results: results,
      citation: citation,
      training: training,
      userInitiated: userAgents,
      notes: notes,
      summary: {
        path: path,
        fileIsEmpty: fileIsEmpty,
        groups: parsed.groups.length,
        sitemaps: parsed.sitemaps.length,
        citationAllowed: citation.length - citationBlocked.length,
        citationTotal: citation.length,
        citationBlocked: citationBlocked.length,
        trainingAllowed: training.length - trainingBlocked.length,
        trainingTotal: training.length,
        trainingBlocked: trainingBlocked.length,
        userAllowed: userAgents.length - userBlocked.length,
        userTotal: userAgents.length,
        posture: posture,
        postureLabel: postureLabel,
        grade: grade
      }
    };
  }

  return {
    check: check,
    parse: parse,
    selectGroup: selectGroup,
    evaluate: evaluate,
    AGENTS: AGENTS,
    PURPOSE: { CITE: CITE, TRAIN: TRAIN, USER: USER }
  };
});
