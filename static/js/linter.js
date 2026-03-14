/* Technical Writing Linter
   ninadpathak.com/linter/
   Pure client-side. No server. No tracking. Vanilla JS. */

(function () {
  'use strict';

  // ─────────────────────────────────────────────────────────────────────
  // RULE DEFINITIONS
  // ─────────────────────────────────────────────────────────────────────

  var RULES = [

    // ── ERRORS ──────────────────────────────────────────────────────────

    {
      id: 'condescension',
      severity: 'error',
      label: 'Condescension',
      terms: [
        'simply', 'just', 'easy', 'easily', 'obvious', 'obviously',
        'trivial', 'trivially', 'of course', 'needless to say',
        'as everyone knows', "it's clear that", 'it is clear that'
      ],
      message: function (w) {
        return '"' + w + '" assumes the reader already knows this. Remove it.';
      }
    },

    {
      id: 'ai_signal',
      severity: 'error',
      label: 'AI writing signal',
      terms: [
        'delve', 'delves', 'delving', 'dive deep', 'dives deep',
        'in conclusion', 'in summary', 'to summarize', 'to conclude',
        "it's worth noting", 'it is worth noting',
        'it should be noted', 'it is important to note',
        "in today's", 'in today\'s fast-paced',
        'rapidly evolving', 'ever-evolving', 'fast-paced world',
        'unlock the potential', 'unlock the power',
        'harness the power', 'harness the potential',
        'navigate the complexities', 'the world of',
        'landscape of', 'realm of'
      ],
      message: function (w) {
        return '"' + w + '" is a hallmark of LLM-generated content. Cut it.';
      }
    },

    {
      id: 'filler_opener',
      severity: 'error',
      label: 'Filler opener',
      terms: [
        'in this article', 'in this post', 'in this tutorial',
        'in this guide', 'in this blog post', 'in this write-up',
        'welcome to this', 'today we will', 'today you will',
        "today we're going to", "today we are going to",
        'by the end of this', 'in this comprehensive'
      ],
      message: function (w) {
        return '"' + w + '" announces the article instead of starting it. Open with something true.';
      }
    },

    // ── WARNINGS ─────────────────────────────────────────────────────────

    {
      id: 'hedge',
      severity: 'warning',
      label: 'Hedge word',
      terms: [
        'very', 'really', 'quite', 'basically', 'fairly',
        'rather', 'somewhat', 'pretty much', 'kind of', 'sort of'
      ],
      message: function (w) {
        return '"' + w + '" weakens the sentence. Remove it or make a stronger claim.';
      }
    },

    {
      id: 'buzzword',
      severity: 'warning',
      label: 'Buzzword',
      terms: [
        'leverage', 'leverages', 'leveraging', 'leveraged',
        'synergy', 'synergies', 'synergistic',
        'cutting-edge', 'state-of-the-art',
        'seamless', 'seamlessly',
        'robust', 'robustly',
        'game-changing', 'game changer',
        'innovative', 'groundbreaking',
        'utilize', 'utilizes', 'utilizing', 'utilized',
        'paradigm shift', 'mission-critical',
        'best-in-class', 'next-generation', 'next generation'
      ],
      message: function (w) {
        return '"' + w + '" is a buzzword. Use the plain-language version.';
      }
    },

    {
      id: 'filler_phrase',
      severity: 'warning',
      label: 'Filler phrase',
      terms: [
        'in order to', 'note that', 'please note', 'as you can see',
        'and so on', 'at this point in time',
        'at the end of the day', 'the fact that',
        'due to the fact that', 'as a matter of fact',
        'in the event that'
      ],
      message: function (w) {
        return '"' + w + '" adds no meaning. Cut it.';
      }
    },

    {
      id: 'tutorial_we',
      severity: 'warning',
      label: 'Tutorial "we"',
      terms: [
        'we will', "we'll", "let's", 'let us',
        'we need to', 'we can', 'we should',
        'we want to', 'we are going to', "we're going to"
      ],
      message: function (w) {
        return '"' + w + '" puts the writer in the tutorial. Address the reader with "you".';
      }
    }

  ];

  // ─────────────────────────────────────────────────────────────────────
  // TEXT HELPERS
  // ─────────────────────────────────────────────────────────────────────

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function getLineNumber(text, index) {
    return text.substring(0, index).split('\n').length;
  }

  function getExcerpt(text, index, length) {
    var start   = Math.max(0, index - 15);
    var end     = Math.min(text.length, index + length + 30);
    var excerpt = text.substring(start, end).replace(/\n/g, ' ').trim();
    if (start > 0)         excerpt = '\u2026' + excerpt;
    if (end < text.length) excerpt = excerpt + '\u2026';
    return excerpt;
  }

  function getSentences(text) {
    // Split on . ! ? followed by whitespace+capital, or end of string
    // Good enough for linting purposes; won't be perfect on abbreviations
    var parts = text
      .replace(/([.!?])\s+(?=[A-Z"'])/g, '$1\n')
      .split('\n')
      .map(function (s) { return s.trim(); })
      .filter(function (s) { return s.length > 3; });
    return parts.length > 0 ? parts : [text];
  }

  function countSyllables(word) {
    word = word.toLowerCase().replace(/[^a-z]/g, '');
    if (!word) return 0;
    if (word.length <= 3) return 1;
    word = word.replace(/(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$/, '');
    word = word.replace(/^y/, '');
    var groups = word.match(/[aeiouy]{1,2}/g);
    return groups ? Math.max(1, groups.length) : 1;
  }

  function fleschKincaid(text) {
    var wordList  = text.match(/\b[a-zA-Z'-]+\b/g) || [];
    if (wordList.length < 20) return null;
    var sentences = getSentences(text);
    var totalSyl  = wordList.reduce(function (s, w) { return s + countSyllables(w); }, 0);
    var avgWPS    = wordList.length / Math.max(1, sentences.length);
    var avgSPW    = totalSyl / wordList.length;
    var score     = 206.835 - 1.015 * avgWPS - 84.6 * avgSPW;
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  // ─────────────────────────────────────────────────────────────────────
  // SPECIAL CHECKS (not simple term lists)
  // ─────────────────────────────────────────────────────────────────────

  function findPassiveVoice(text) {
    var issues = [];
    // (is|are|was|were|be|been|being) + optional adverb + past participle
    var re = /\b(is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+ed)\b/gi;
    var m;
    while ((m = re.exec(text)) !== null) {
      issues.push({ index: m.index, length: m[0].length, matched: m[0] });
    }
    return issues;
  }

  function findLongSentences(text) {
    var issues    = [];
    var LIMIT     = 35;
    var sentences = getSentences(text);
    var cursor    = 0;

    for (var i = 0; i < sentences.length; i++) {
      var s  = sentences[i];
      var wc = (s.match(/\b\w+\b/g) || []).length;
      var idx = text.indexOf(s, cursor);
      if (idx === -1) idx = cursor;
      cursor = idx + s.length;

      if (wc > LIMIT) {
        issues.push({ index: idx, length: s.length, matched: s, wordCount: wc });
      }
    }
    return issues;
  }

  // ─────────────────────────────────────────────────────────────────────
  // CORE LINT FUNCTION
  // ─────────────────────────────────────────────────────────────────────

  function lint(text) {
    var allIssues = [];

    // ── Term-based rules ──────────────────────────────────────────────
    for (var ri = 0; ri < RULES.length; ri++) {
      var rule = RULES[ri];
      for (var ti = 0; ti < rule.terms.length; ti++) {
        var term     = rule.terms[ti];
        var isPhrase = term.indexOf(' ') !== -1 || term.indexOf('-') !== -1;
        var pattern  = isPhrase
          ? new RegExp(escapeRegex(term), 'gi')
          : new RegExp('\\b' + escapeRegex(term) + '\\b', 'gi');

        var m;
        while ((m = pattern.exec(text)) !== null) {
          allIssues.push({
            severity: rule.severity,
            rule:     rule.id,
            label:    rule.label,
            matched:  m[0],
            excerpt:  getExcerpt(text, m.index, m[0].length),
            line:     getLineNumber(text, m.index),
            message:  rule.message(m[0])
          });
        }
      }
    }

    // ── Passive voice ─────────────────────────────────────────────────
    var passives = findPassiveVoice(text);
    for (var pi = 0; pi < passives.length; pi++) {
      var pv = passives[pi];
      allIssues.push({
        severity: 'info',
        rule:     'passive_voice',
        label:    'Possible passive voice',
        matched:  pv.matched,
        excerpt:  getExcerpt(text, pv.index, pv.length),
        line:     getLineNumber(text, pv.index),
        message:  'Passive construction. Rewrite with an active subject if possible.'
      });
    }

    // ── Long sentences ────────────────────────────────────────────────
    var longSents = findLongSentences(text);
    for (var li = 0; li < longSents.length; li++) {
      var ls = longSents[li];
      allIssues.push({
        severity: 'info',
        rule:     'long_sentence',
        label:    'Long sentence',
        matched:  ls.matched,
        excerpt:  getExcerpt(text, ls.index, Math.min(ls.length, 70)),
        line:     getLineNumber(text, ls.index),
        message:  ls.wordCount + '-word sentence. Technical readers scan. Break this up.'
      });
    }

    // ── Document-level: adverb density ───────────────────────────────
    var words   = text.match(/\b\w+\b/g) || [];
    var adverbs = words.filter(function (w) { return w.length > 3 && /ly$/i.test(w); });
    var advPct  = words.length > 0 ? adverbs.length / words.length : 0;
    if (advPct > 0.05 && words.length > 50) {
      allIssues.push({
        severity: 'info',
        rule:     'adverb_density',
        label:    'High adverb density',
        matched:  Math.round(advPct * 100) + '%',
        excerpt:  Math.round(advPct * 100) + '% of words are adverbs (' + adverbs.length + ' found)',
        line:     null,
        message:  'High adverb count signals over-modified prose. Target under 5%.'
      });
    }

    // ── Document-level: readability ───────────────────────────────────
    var fkScore = fleschKincaid(text);
    if (fkScore !== null && fkScore < 30) {
      allIssues.push({
        severity: 'info',
        rule:     'readability',
        label:    'Low readability',
        matched:  'FK: ' + fkScore,
        excerpt:  'Flesch-Kincaid score: ' + fkScore + '/100 (very hard to read)',
        line:     null,
        message:  'Plain-language standards target 60+. Shorten sentences, use simpler words.'
      });
    }

    // ── Sort by line ──────────────────────────────────────────────────
    allIssues.sort(function (a, b) {
      if (a.line === null && b.line === null) return 0;
      if (a.line === null) return 1;
      if (b.line === null) return -1;
      return a.line - b.line;
    });

    var errors   = allIssues.filter(function (i) { return i.severity === 'error'; });
    var warnings = allIssues.filter(function (i) { return i.severity === 'warning'; });
    var infos    = allIssues.filter(function (i) { return i.severity === 'info'; });

    // Score: start at 100, penalise per issue (capped to avoid going below 0)
    var penalty = errors.length * 8 + warnings.length * 4 + infos.length * 2;
    var score   = Math.max(0, 100 - penalty);

    var grade, gradeDesc;
    if      (score >= 90) { grade = 'A'; gradeDesc = 'Publish it.'; }
    else if (score >= 80) { grade = 'B'; gradeDesc = 'Minor issues.'; }
    else if (score >= 65) { grade = 'C'; gradeDesc = 'Needs editing.'; }
    else if (score >= 50) { grade = 'D'; gradeDesc = 'Significant issues.'; }
    else                  { grade = 'F'; gradeDesc = 'Rewrite it.'; }

    var sentences = getSentences(text);

    return {
      score:     score,
      grade:     grade,
      gradeDesc: gradeDesc,
      fkScore:   fkScore,
      wordCount: words.length,
      sentCount: sentences.length,
      issues:    allIssues,
      errors:    errors,
      warnings:  warnings,
      infos:     infos
    };
  }

  // ─────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderResults(result) {
    var scoreEl    = document.getElementById('lintScore');
    var gradeEl    = document.getElementById('lintGrade');
    var gradeDescEl = document.getElementById('lintGradeDesc');
    var statsEl    = document.getElementById('lintStats');
    var scoreBarEl = document.getElementById('lintScoreBar');
    var issuesEl   = document.getElementById('lintIssues');

    scoreEl.textContent    = result.score;
    gradeEl.textContent    = result.grade;
    gradeDescEl.textContent = result.gradeDesc;

    // Grade colour via class
    scoreBarEl.className = 'lint-score-bar lint-grade-' + result.grade.toLowerCase();

    // Stats row
    var statsHtml = [
      '<span>' + result.wordCount + ' words</span>',
      '<span class="lint-stat-sep">\u00b7</span>',
      '<span>' + result.sentCount + ' sentences</span>',
      '<span class="lint-stat-sep">\u00b7</span>',
      '<span>' + result.issues.length + ' issue' + (result.issues.length !== 1 ? 's' : '') + '</span>'
    ];
    if (result.fkScore !== null) {
      statsHtml.push('<span class="lint-stat-sep">\u00b7</span>');
      statsHtml.push('<span>FK\u00a0' + result.fkScore + '</span>');
    }
    statsEl.innerHTML = statsHtml.join('');

    // Issues
    var html = '';

    if (result.issues.length === 0) {
      html = '<div class="lint-clean"><span>\u2714</span> No issues found. Either this is excellent writing or the linter missed something.</div>';
    } else {
      var groups = [
        { severity: 'error',   label: 'Errors',   icon: '\u25cf', items: result.errors },
        { severity: 'warning', label: 'Warnings', icon: '\u25b2', items: result.warnings },
        { severity: 'info',    label: 'Info',      icon: '\u2139', items: result.infos }
      ];

      for (var gi = 0; gi < groups.length; gi++) {
        var g = groups[gi];
        if (g.items.length === 0) continue;

        html += '<div class="lint-group">';
        html += '<div class="lint-group-header lint-group-' + g.severity + '">';
        html += '<span class="lint-sev-icon">' + g.icon + '</span>';
        html += '<span class="lint-group-label">' + g.label + '</span>';
        html += '<span class="lint-group-count">' + g.items.length + '</span>';
        html += '</div>';
        html += '<div class="lint-group-items">';

        for (var ii = 0; ii < g.items.length; ii++) {
          var issue = g.items[ii];
          html += '<div class="lint-item lint-item-' + issue.severity + '">';
          html += '<div class="lint-item-meta">';
          html += '<span class="lint-item-rule">' + escapeHtml(issue.label) + '</span>';
          if (issue.line !== null) {
            html += '<span class="lint-item-line">L' + issue.line + '</span>';
          }
          html += '</div>';
          html += '<div class="lint-item-excerpt">\u201c' + escapeHtml(issue.excerpt) + '\u201d</div>';
          html += '<div class="lint-item-message">' + escapeHtml(issue.message) + '</div>';
          html += '</div>';
        }

        html += '</div></div>';
      }
    }

    issuesEl.innerHTML = html;

    document.getElementById('linterOutput').hidden = false;
    document.getElementById('linterEmpty').hidden  = true;
  }

  // ─────────────────────────────────────────────────────────────────────
  // COPY RESULTS
  // ─────────────────────────────────────────────────────────────────────

  function buildCopyText(result) {
    var lines = [
      'Technical Writing Linter \u2014 ninadpathak.com/linter/',
      '',
      'Score: ' + result.score + '/100 (' + result.grade + ') \u2014 ' + result.gradeDesc,
      result.wordCount + ' words \u00b7 ' + result.sentCount + ' sentences \u00b7 ' + result.issues.length + ' issues',
      ''
    ];

    if (result.errors.length) {
      lines.push('\u25cf Errors (' + result.errors.length + ')');
      result.errors.slice(0, 6).forEach(function (i) {
        lines.push('  ' + i.label + (i.line ? ' \u00b7 L' + i.line : '') + ' \u2014 ' + i.excerpt);
      });
      lines.push('');
    }
    if (result.warnings.length) {
      lines.push('\u25b2 Warnings (' + result.warnings.length + ')');
      result.warnings.slice(0, 6).forEach(function (i) {
        lines.push('  ' + i.label + (i.line ? ' \u00b7 L' + i.line : '') + ' \u2014 ' + i.excerpt);
      });
      lines.push('');
    }
    if (result.infos.length) {
      lines.push('\u2139 Info (' + result.infos.length + ')');
      result.infos.slice(0, 4).forEach(function (i) {
        lines.push('  ' + i.label + (i.line ? ' \u00b7 L' + i.line : '') + ' \u2014 ' + i.excerpt);
      });
      lines.push('');
    }

    return lines.join('\n');
  }

  // ─────────────────────────────────────────────────────────────────────
  // SAMPLE ARTICLE  (intentionally bad — loads up the linter nicely)
  // ─────────────────────────────────────────────────────────────────────

  var SAMPLE = [
    'In this tutorial, we will learn how to simply set up JWT authentication in Node.js.',
    '',
    "It's worth noting that authentication is a very important part of any web application.",
    'We will leverage the robust jsonwebtoken library to seamlessly handle tokens.',
    'This guide will delve into the cutting-edge approaches that modern developers are utilizing.',
    '',
    "Of course, you'll need Node.js installed. This is quite easy to do.",
    'Just run npm install and you should basically be good to go.',
    '',
    "In today's rapidly evolving tech landscape, it is important to note that security matters.",
    "We'll explore how to harness the power of JWT to unlock the potential of your API.",
    '',
    'The token validation process is handled by the middleware, which is called on every protected route.',
    'In order to verify a token, the secret key is compared against the signature that was embedded in the JWT.',
    '',
    'Please note that sensitive data should never be stored in the payload.',
    'As you can see, the implementation is quite straightforward once you understand the underlying concepts.',
  ].join('\n');

  // ─────────────────────────────────────────────────────────────────────
  // INIT
  // ─────────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    var input      = document.getElementById('linterInput');
    var lintBtn    = document.getElementById('lintBtn');
    var sampleBtn  = document.getElementById('loadSample');
    var copyBtn    = document.getElementById('copyResults');
    var clearBtn   = document.getElementById('clearLinter');
    var charCount  = document.getElementById('charCount');

    if (!input || !lintBtn) return;

    var lastResult = null;

    function updateWordCount() {
      var wc = (input.value.match(/\b\w+\b/g) || []).length;
      charCount.textContent = wc + ' word' + (wc !== 1 ? 's' : '');
    }

    input.addEventListener('input', updateWordCount);

    if (sampleBtn) {
      sampleBtn.addEventListener('click', function () {
        input.value = SAMPLE;
        updateWordCount();
        input.focus();
      });
    }

    lintBtn.addEventListener('click', function () {
      var text = input.value.trim();
      if (!text) { input.focus(); return; }
      lastResult = lint(text);
      renderResults(lastResult);
      document.getElementById('linterOutput').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    // Cmd/Ctrl + Enter to run
    input.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        lintBtn.click();
      }
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (!lastResult) return;
        var text = buildCopyText(lastResult);
        navigator.clipboard.writeText(text).then(function () {
          var orig = copyBtn.textContent;
          copyBtn.textContent = 'Copied!';
          setTimeout(function () { copyBtn.textContent = orig; }, 2000);
        }).catch(function () {
          // fallback: select a temp element
          var ta = document.createElement('textarea');
          ta.value = text;
          ta.style.position = 'fixed';
          ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          copyBtn.textContent = 'Copied!';
          setTimeout(function () { copyBtn.textContent = 'Copy Results'; }, 2000);
        });
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        input.value = '';
        updateWordCount();
        document.getElementById('linterOutput').hidden = true;
        document.getElementById('linterEmpty').hidden  = false;
        lastResult = null;
        input.focus();
      });
    }
  });

}());
