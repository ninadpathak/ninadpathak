/*
 * AI crawler access checker — browser wiring.
 *
 * All rules live in robots-access-core.js. This file moves text between the DOM
 * and that engine and renders results with the existing linter.css vocabulary.
 * No CSS is added anywhere.
 *
 * Privacy contract, enforced by construction:
 *   - The paste path calls the engine directly. Pasted text never leaves the
 *     page: no fetch, no beacon, no storage on that path.
 *   - The domain path posts only a domain to /api/fetch-robots, which needs a
 *     server hop because a browser cannot read another origin's robots.txt.
 */
(function () {
  "use strict";

  var core = window.RobotsAccessCore;
  if (!core) return;

  var input = document.getElementById("robotsInput");
  var runBtn = document.getElementById("robotsRunBtn");
  var clearBtn = document.getElementById("robotsClear");
  var copyBtn = document.getElementById("robotsCopy");
  var sampleBtn = document.getElementById("robotsSample");
  var charCount = document.getElementById("robotsCharCount");
  var pathInput = document.getElementById("robotsPath");

  var emptyState = document.getElementById("robotsEmpty");
  var resultsState = document.getElementById("robotsResults");
  var scoreBar = document.getElementById("robotsScoreBar");
  var scoreNumber = document.getElementById("robotsScoreNumber");
  var postureEl = document.getElementById("robotsPosture");
  var postureDescEl = document.getElementById("robotsPostureDesc");
  var statsEl = document.getElementById("robotsStats");
  var findingsEl = document.getElementById("robotsFindings");

  var domainForm = document.getElementById("robotsDomainForm");
  var domainInput = document.getElementById("robotsDomain");
  var domainStatus = document.getElementById("robotsDomainStatus");

  var lastResult = null;

  var SAMPLE = [
    "# A training opt-out that keeps every citation crawler.",
    "# This is the shape most publishers actually want.",
    "",
    "User-agent: *",
    "Allow: /",
    "",
    "User-agent: GPTBot",
    "Disallow: /",
    "",
    "User-agent: ClaudeBot",
    "Disallow: /",
    "",
    "User-agent: Google-Extended",
    "Disallow: /",
    "",
    "User-agent: CCBot",
    "Disallow: /",
    "",
    "Sitemap: https://example.com/sitemap.xml",
    ""
  ].join("\n");

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function readInput() {
    return input ? input.innerText || input.textContent || "" : "";
  }

  function currentPath() {
    var value = pathInput ? pathInput.value.trim() : "";
    if (!value) return "/";
    return value.charAt(0) === "/" ? value : "/" + value;
  }

  function updateCharCount() {
    if (!charCount) return;
    var text = readInput();
    var lines = text.trim() === "" ? 0 : text.split(/\r\n|\n|\r/).length;
    charCount.textContent = lines + (lines === 1 ? " line" : " lines");
  }

  function setDomainStatus(message, state) {
    if (!domainStatus) return;
    domainStatus.textContent = message || "";
    domainStatus.className = "tool-status" + (state ? " tool-status-" + state : "");
  }

  var SECTIONS = [
    {
      key: "citation",
      severity: "error",
      label: "citation crawlers",
      caption: "These decide whether a platform may quote the page in an answer. A block here removes the site from that platform's answers."
    },
    {
      key: "userInitiated",
      severity: "warning",
      label: "user-initiated fetches",
      caption: "These fetch a page when a person asks the assistant a question that needs it."
    },
    {
      key: "training",
      severity: "info",
      label: "training crawlers",
      caption: "These decide whether content may be used to train a model. Blocking them is a legitimate choice and does not affect citation."
    }
  ];

  function render(result) {
    lastResult = result;
    if (emptyState) emptyState.hidden = true;
    if (resultsState) resultsState.hidden = false;

    var summary = result.summary;
    if (scoreNumber) scoreNumber.textContent = summary.citationAllowed + "/" + summary.citationTotal;
    if (postureEl) postureEl.textContent = summary.posture;
    if (postureDescEl) postureDescEl.textContent = summary.postureLabel;
    if (scoreBar) scoreBar.className = "lint-score-bar lint-grade-" + summary.grade;

    if (statsEl) {
      var parts = [
        "citation " + summary.citationAllowed + "/" + summary.citationTotal,
        "training " + summary.trainingAllowed + "/" + summary.trainingTotal,
        summary.groups + (summary.groups === 1 ? " group" : " groups"),
        "path " + summary.path
      ];
      statsEl.innerHTML = parts.join(' <span class="lint-stat-sep">&middot;</span> ');
    }

    if (!findingsEl) return;

    var html = "";

    SECTIONS.forEach(function (section) {
      var items = result[section.key] || [];
      if (!items.length) return;
      var blocked = items.filter(function (item) { return !item.allowed; }).length;
      html += '<div class="lint-group lint-group-' + section.severity + '">';
      html += '<div class="lint-group-header"><span class="lint-group-label">' +
        escapeHtml(section.label) + " — " + (items.length - blocked) + " of " + items.length +
        " allowed</span></div>";
      html += '<div class="lint-item"><div class="lint-item-message">' +
        escapeHtml(section.caption) + "</div></div>";
      items.forEach(function (item) {
        html += '<div class="lint-item">';
        html += '<div class="lint-item-meta">';
        html += '<span class="lint-item-rule">' + escapeHtml(item.token) + "</span>";
        html += '<span class="lint-item-line">' + (item.allowed ? "allowed" : "blocked") + "</span>";
        html += "</div>";
        html += '<div class="lint-item-message"><strong>' + escapeHtml(item.platform) + ".</strong> " +
          escapeHtml(item.note) + "</div>";
        html += '<div class="lint-item-excerpt">' + escapeHtml(item.explanation) + "</div>";
        html += '<div class="lint-item-message"><strong>Source:</strong> ' + escapeHtml(item.source) + "</div>";
        html += "</div>";
      });
      html += "</div>";
    });

    if (result.notes && result.notes.length) {
      var warnings = result.notes.filter(function (note) { return note.severity === "warning"; });
      var infos = result.notes.filter(function (note) { return note.severity !== "warning"; });
      [
        { items: warnings, severity: "warning", label: "file problems" },
        { items: infos, severity: "info", label: "notes and limits" }
      ].forEach(function (group) {
        if (!group.items.length) return;
        html += '<div class="lint-group lint-group-' + group.severity + '">';
        html += '<div class="lint-group-header"><span class="lint-group-label">' +
          escapeHtml(group.label) + " (" + group.items.length + ")</span></div>";
        group.items.forEach(function (note) {
          html += '<div class="lint-item">';
          html += '<div class="lint-item-meta"><span class="lint-item-rule">' + escapeHtml(note.id) + "</span>";
          if (typeof note.line === "number") {
            html += '<span class="lint-item-line">line ' + note.line + "</span>";
          }
          html += "</div>";
          if (note.excerpt) {
            html += '<div class="lint-item-excerpt">' + escapeHtml(note.excerpt) + "</div>";
          }
          html += '<div class="lint-item-message">' + escapeHtml(note.message) + "</div>";
          html += '<div class="lint-item-message"><strong>Based on:</strong> ' + escapeHtml(note.basis) + "</div>";
          html += "</div>";
        });
        html += "</div>";
      });
    }

    findingsEl.innerHTML = html;
  }

  function run() {
    render(core.check(readInput(), { path: currentPath() }));
  }

  function setInput(text) {
    if (!input) return;
    input.textContent = text;
    updateCharCount();
  }

  if (runBtn) runBtn.addEventListener("click", run);
  if (pathInput) {
    pathInput.addEventListener("change", function () {
      if (lastResult) run();
    });
  }

  if (input) {
    input.addEventListener("input", updateCharCount);
    input.addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        run();
      }
    });
    input.addEventListener("paste", function (event) {
      event.preventDefault();
      var text = (event.clipboardData || window.clipboardData).getData("text/plain");
      document.execCommand("insertText", false, text);
    });
  }

  if (sampleBtn) {
    sampleBtn.addEventListener("click", function () {
      setInput(SAMPLE);
      run();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      setInput("");
      lastResult = null;
      if (resultsState) resultsState.hidden = true;
      if (emptyState) emptyState.hidden = false;
      setDomainStatus("");
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      if (!lastResult || !navigator.clipboard) return;
      var summary = lastResult.summary;
      var lines = [
        "AI crawler access report",
        "path checked: " + summary.path,
        "citation crawlers allowed: " + summary.citationAllowed + " of " + summary.citationTotal,
        "training crawlers allowed: " + summary.trainingAllowed + " of " + summary.trainingTotal,
        "This reads robots.txt only. A CDN or WAF can block a crawler at the edge regardless.",
        ""
      ];
      lastResult.results.forEach(function (item) {
        lines.push("[" + (item.allowed ? "allowed" : "blocked") + "/" + item.purpose + "] " +
          item.token + " — " + item.platform);
        lines.push("    " + item.explanation);
      });
      navigator.clipboard.writeText(lines.join("\n")).then(function () {
        copyBtn.textContent = "copied";
        setTimeout(function () { copyBtn.textContent = "copy"; }, 1500);
      });
    });
  }

  if (domainForm) {
    domainForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var value = domainInput ? domainInput.value.trim() : "";
      if (!value) {
        setDomainStatus("Enter a domain to check.", "error");
        return;
      }
      setDomainStatus("Fetching robots.txt…", "loading");
      fetch("/api/fetch-robots", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: value })
      })
        .then(function (response) {
          return response.json().then(function (body) {
            if (!response.ok) throw new Error(body.error || "That robots.txt could not be fetched.");
            return body;
          });
        })
        .then(function (body) {
          // An absent file is a real answer, not a failure: nothing is disallowed.
          if (body.absent) {
            setInput("");
            setDomainStatus(body.message, "success");
            run();
            return;
          }
          if (!body.found) {
            setDomainStatus(body.error || "That robots.txt could not be fetched.", "error");
            return;
          }
          setInput(body.content);
          if (body.servedAsHtml) {
            setDomainStatus(
              body.finalUrl + " returned HTML rather than a text file. Crawlers cannot parse that, " +
              "so the rules below are unlikely to be what the site intends.",
              "error"
            );
          } else {
            var note = "Read " + body.finalUrl + " (" + body.bytes + " bytes).";
            if (body.leftOriginalSite) {
              note += " That is a different site from the domain you entered, and robots.txt applies per origin, " +
                "so these rules belong to the redirect target.";
            }
            setDomainStatus(note, "success");
          }
          run();
        })
        .catch(function (error) {
          setDomainStatus(error.message || "That robots.txt could not be fetched.", "error");
        });
    });
  }

  updateCharCount();
})();
