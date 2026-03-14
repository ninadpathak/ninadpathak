/* Technical Writing Linter
   ninadpathak.com/linter/
   Pure client-side. No server. No tracking. Vanilla JS. */

(function () {
  'use strict';

  // ─────────────────────────────────────────────────────────────────────
  // RULE DEFINITIONS
  // ─────────────────────────────────────────────────────────────────────

  var RULES = [
    {
      id: 'condescension',
      severity: 'error',
      label: 'Condescension',
      terms: [
        'simply', 'just', 'easy', 'easily', 'obvious', 'obviously',
        'trivial', 'trivially', 'of course', 'needless to say',
        'as everyone knows', "it's clear that", 'it is clear that'
      ],
      message: function (w) { return '"' + w + '" assumes the reader already knows this. Remove it.'; }
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
      message: function (w) { return '"' + w + '" is a hallmark of LLM-generated content. Cut it.'; }
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
      message: function (w) { return '"' + w + '" announces the article instead of starting it.'; }
    },
    {
      id: 'hedge',
      severity: 'warning',
      label: 'Hedge word',
      terms: [
        'very', 'really', 'quite', 'basically', 'fairly',
        'rather', 'somewhat', 'pretty much', 'kind of', 'sort of'
      ],
      message: function (w) { return '"' + w + '" weakens the sentence. Remove it.'; }
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
        'best-in-class', 'next-generation'
      ],
      message: function (w) { return '"' + w + '" is a buzzword. Use plain language.'; }
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
      message: function (w) { return '"' + w + '" adds no meaning. Cut it.'; }
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
      message: function (w) { return '"' + w + '" puts the writer in the tutorial. Address the reader directly.'; }
    }
  ];

  // ─────────────────────────────────────────────────────────────────────
  // TEXT HELPERS
  // ─────────────────────────────────────────────────────────────────────

  function escapeRegex(str) { return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  
  function getExcerpt(text, index, length) {
    var start = Math.max(0, index - 15);
    var end = Math.min(text.length, index + length + 20);
    var excerpt = text.substring(start, end).replace(/\n/g, ' ').trim();
    if (start > 0) excerpt = '\u2026' + excerpt;
    if (end < text.length) excerpt = excerpt + '\u2026';
    return excerpt;
  }

  function getSentences(text) {
    return text.replace(/([.!?])\s+(?=[A-Z"'])/g, '$1\n').split('\n').filter(function (s) { return s.trim().length > 3; });
  }

  function countSyllables(word) {
    word = word.toLowerCase().replace(/[^a-z]/g, '');
    if (!word || word.length <= 3) return 1;
    word = word.replace(/(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$/, '').replace(/^y/, '');
    var groups = word.match(/[aeiouy]{1,2}/g);
    return groups ? Math.max(1, groups.length) : 1;
  }

  function fleschKincaid(text) {
    var wordList = text.match(/\b[a-zA-Z'-]+\b/g) || [];
    if (wordList.length < 20) return null;
    var sentences = getSentences(text);
    var totalSyl = wordList.reduce(function (s, w) { return s + countSyllables(w); }, 0);
    var score = 206.835 - 1.015 * (wordList.length / Math.max(1, sentences.length)) - 84.6 * (totalSyl / wordList.length);
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  function findPassiveVoice(text) {
    var issues = [];
    var re = /\b(is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+ed)\b/gi;
    var m;
    while ((m = re.exec(text)) !== null) {
      issues.push({ index: m.index, length: m[0].length, matched: m[0] });
    }
    return issues;
  }

  function findLongSentences(text) {
    var issues = [];
    var sentences = getSentences(text);
    var cursor = 0;
    for (var i = 0; i < sentences.length; i++) {
      var s = sentences[i];
      var wc = (s.match(/\b\w+\b/g) || []).length;
      var idx = text.indexOf(s, cursor);
      if (idx === -1) idx = cursor;
      cursor = idx + s.length;
      if (wc > 35) issues.push({ index: idx, length: s.length, matched: s, wordCount: wc });
    }
    return issues;
  }

  // ─────────────────────────────────────────────────────────────────────
  // CORE LINT
  // ─────────────────────────────────────────────────────────────────────

  function lint(text) {
    var allIssues = [];

    // Term-based
    RULES.forEach(function(rule) {
      rule.terms.forEach(function(term) {
        var isPhrase = term.indexOf(' ') !== -1 || term.indexOf('-') !== -1;
        var pattern = isPhrase ? new RegExp(escapeRegex(term), 'gi') : new RegExp('\\b' + escapeRegex(term) + '\\b', 'gi');
        var m;
        while ((m = pattern.exec(text)) !== null) {
          allIssues.push({
            id: 'issue-' + Math.random().toString(36).substr(2, 9),
            index: m.index,
            length: m[0].length,
            severity: rule.severity,
            rule: rule.id,
            label: rule.label,
            matched: m[0],
            excerpt: getExcerpt(text, m.index, m[0].length),
            message: rule.message(m[0])
          });
        }
      });
    });

    // Passive voice
    findPassiveVoice(text).forEach(function(pv) {
      allIssues.push({
        id: 'issue-' + Math.random().toString(36).substr(2, 9),
        index: pv.index,
        length: pv.length,
        severity: 'info',
        rule: 'passive_voice',
        label: 'Passive voice',
        matched: pv.matched,
        excerpt: getExcerpt(text, pv.index, pv.length),
        message: 'Rewrite with an active subject if possible.'
      });
    });

    // Long sentences
    findLongSentences(text).forEach(function(ls) {
      allIssues.push({
        id: 'issue-' + Math.random().toString(36).substr(2, 9),
        index: ls.index,
        length: ls.length,
        severity: 'info',
        rule: 'long_sentence',
        label: 'Long sentence',
        matched: ls.matched,
        excerpt: getExcerpt(text, ls.index, Math.min(ls.length, 50)),
        message: ls.wordCount + ' words. Break this up.'
      });
    });

    allIssues.sort(function(a, b) { return a.index - b.index; });

    var words = text.match(/\b\w+\b/g) || [];
    var fk = fleschKincaid(text);
    var penalty = allIssues.filter(i => i.severity === 'error').length * 8 + 
                  allIssues.filter(i => i.severity === 'warning').length * 4 + 
                  allIssues.filter(i => i.severity === 'info').length * 2;
    var score = Math.max(0, 100 - penalty);
    var grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 65 ? 'C' : score >= 50 ? 'D' : 'F';
    var gradeDesc = score >= 90 ? 'Publish it.' : score >= 80 ? 'Minor issues.' : score >= 65 ? 'Needs editing.' : score >= 50 ? 'Significant issues.' : 'Rewrite it.';

    return {
      score: score,
      grade: grade,
      gradeDesc: gradeDesc,
      fkScore: fk,
      wordCount: words.length,
      issues: allIssues
    };
  }

  // ─────────────────────────────────────────────────────────────────────
  // DOM & INTERACTION
  // ─────────────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function renderHighlitContent(text, issues) {
    var result = '';
    var lastIndex = 0;
    // Overlapping issues check - simple version: sort and skip overlaps
    var sorted = issues.slice().sort((a,b) => a.index - b.index);
    
    sorted.forEach(function(issue) {
      if (issue.index < lastIndex) return; // Skip overlaps
      result += escapeHtml(text.substring(lastIndex, issue.index));
      result += '<span class="lint-highlight highlight-' + issue.severity + '" data-issue-id="' + issue.id + '">' + 
                escapeHtml(text.substring(issue.index, issue.index + issue.length)) + '</span>';
      lastIndex = issue.index + issue.length;
    });
    result += escapeHtml(text.substring(lastIndex));
    return result;
  }

  function renderResults(result) {
    var issuesEl = document.getElementById('lintIssues');
    var scoreBarEl = document.getElementById('lintScoreBar');
    
    document.getElementById('lintScore').textContent = result.score;
    document.getElementById('lintGrade').textContent = result.grade;
    document.getElementById('lintGradeDesc').textContent = result.gradeDesc;
    scoreBarEl.className = 'lint-score-bar lint-grade-' + result.grade.toLowerCase();
    
    document.getElementById('lintStats').innerHTML = result.wordCount + ' words &middot; ' + result.issues.length + ' issues' + (result.fkScore ? ' &middot; FK ' + result.fkScore : '');

    var html = '';
    var groups = [
      { sev: 'error', label: 'Errors', items: result.issues.filter(i => i.severity === 'error') },
      { sev: 'warning', label: 'Warnings', items: result.issues.filter(i => i.severity === 'warning') },
      { sev: 'info', label: 'Info', items: result.issues.filter(i => i.severity === 'info') }
    ];

    groups.forEach(function(g) {
      if (g.items.length === 0) return;
      html += '<div class="lint-group lint-group-' + g.sev + '">';
      html += '<div class="lint-group-header"><span class="lint-group-label">' + g.label + '</span></div>';
      g.items.forEach(function(issue) {
        html += '<div class="lint-item" id="result-' + issue.id + '" data-issue-id="' + issue.id + '">';
        html += '<div class="lint-item-meta"><span class="lint-item-rule">' + escapeHtml(issue.label) + '</span></div>';
        html += '<div class="lint-item-excerpt">&ldquo;' + escapeHtml(issue.matched) + '&rdquo;</div>';
        html += '<div class="lint-item-message">' + escapeHtml(issue.message) + '</div>';
        html += '</div>';
      });
      html += '</div>';
    });

    var container = document.querySelector('.linter-results-container');
    container.scrollTop = 0;

    issuesEl.innerHTML = html || '<div style="padding: 2rem; text-align: center; color: var(--text-3); font-family: var(--mono); font-size: 0.8rem;">No issues found. Perfect.</div>';
    document.getElementById('linterResults').hidden = false;
    document.getElementById('linterEmpty').hidden = true;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var editor = document.getElementById('linterInput');
    var lintBtn = document.getElementById('lintBtn');
    var sampleBtn = document.getElementById('loadSample');
    var clearBtn = document.getElementById('clearLinter');
    var copyBtn = document.getElementById('copyResults');
    var charCount = document.getElementById('charCount');

    if (!editor) return;

    function getCleanText() {
      // Use innerText to get text with line breaks but no HTML tags
      return editor.innerText.replace(/\r/g, '');
    }

    function updateCount() {
      var text = getCleanText();
      var wc = (text.match(/\b\w+\b/g) || []).length;
      charCount.textContent = wc + ' words';
    }

    editor.addEventListener('input', updateCount);

    sampleBtn.addEventListener('click', function() {
      editor.innerText = "In this tutorial, we will learn how to simply set up JWT in Node.js.\n\nIt's worth noting that security is a very important part of any app. We will leverage the robust library to seamlessly handle tokens. This guide will delve into the cutting-edge approaches.\n\nOf course, it is quite easy to do. Just run npm install.";
      updateCount();
    });

    lintBtn.addEventListener('click', function() {
      var text = getCleanText();
      if (!text.trim()) return;
      var result = lint(text);
      editor.innerHTML = renderHighlitContent(text, result.issues);
      renderResults(result);
    });

    // Sync scrolling and clicks
    document.addEventListener('click', function(e) {
      var highlight = e.target.closest('.lint-highlight');
      if (highlight) {
        var id = highlight.getAttribute('data-issue-id');
        var resItem = document.getElementById('result-' + id);
        if (resItem) {
          resItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
          document.querySelectorAll('.lint-item').forEach(i => i.style.background = 'transparent');
          resItem.style.background = 'var(--bg-1)';
        }
      }

      var resItem = e.target.closest('.lint-item');
      if (resItem) {
        var id = resItem.getAttribute('data-issue-id');
        var highlight = editor.querySelector('[data-issue-id="' + id + '"]');
        if (highlight) {
          highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
          highlight.style.outline = '2px solid var(--accent)';
          setTimeout(() => { highlight.style.outline = 'none'; }, 2000);
        }
      }
    });

    clearBtn.addEventListener('click', function() {
      editor.innerHTML = '';
      document.getElementById('linterResults').hidden = true;
      document.getElementById('linterEmpty').hidden = false;
      updateCount();
    });

    copyBtn.addEventListener('click', function() {
      var text = document.getElementById('linterResults').innerText;
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.textContent = 'copied';
        setTimeout(() => { copyBtn.textContent = 'copy'; }, 2000);
      });
    });
  });

})();
