/*
 * AI Overviews checker — browser wiring.
 *
 * All rules live in aio-checker-core.js. This file moves text between the DOM and
 * that engine and renders results with the existing linter.css vocabulary. No CSS
 * is added anywhere.
 *
 * Privacy contract, enforced by construction:
 *   - The paste path calls the engine directly. Pasted content never leaves the
 *     page: no fetch, no beacon, no storage on that path.
 *   - The URL path posts only a URL to /api/fetch-page, which needs a server hop
 *     because a browser cannot read another origin's HTML. The returned HTML is
 *     graded in the browser by the same engine.
 */
(function () {
  "use strict";

  var core = window.AioCheckerCore;
  if (!core) return;

  var input = document.getElementById("aioInput");
  var runBtn = document.getElementById("aioRunBtn");
  var clearBtn = document.getElementById("aioClear");
  var copyBtn = document.getElementById("aioCopy");
  var sampleBtn = document.getElementById("aioSample");
  var charCount = document.getElementById("aioCharCount");

  var emptyState = document.getElementById("aioEmpty");
  var resultsState = document.getElementById("aioResults");
  var scoreBar = document.getElementById("aioScoreBar");
  var scoreNumber = document.getElementById("aioScoreNumber");
  var bandEl = document.getElementById("aioBand");
  var bandDescEl = document.getElementById("aioBandDesc");
  var statsEl = document.getElementById("aioStats");
  var findingsEl = document.getElementById("aioFindings");

  var urlForm = document.getElementById("aioUrlForm");
  var urlInput = document.getElementById("aioUrl");
  var urlStatus = document.getElementById("aioUrlStatus");

  var lastResult = null;
  var pendingOptions = {};

  var SAMPLE = [
    "# Keep one URL per documentation version",
    "",
    "Documentation for multiple versions belongs on one URL per version, with the",
    "current version canonical. Measured across 30 developer docs sites on",
    "2026-08-14, 11 had no version selector at all.",
    "",
    "## A version selector belongs in the page shell, not the sidebar",
    "",
    "A version selector placed in the sidebar disappears on mobile, where the",
    "sidebar collapses. Readers on a phone then cannot tell which version they are",
    "reading.",
    "",
    "## Where this does not apply",
    "",
    "Pre-release documentation is a limitation of this scheme: nightly builds change",
    "too often for stable URLs to be worth maintaining. I did not test this on",
    "monorepos with more than 40 packages.",
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

  function updateCharCount() {
    if (!charCount) return;
    var text = readInput();
    var words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
    charCount.textContent = words + (words === 1 ? " word" : " words");
  }

  function setUrlStatus(message, state) {
    if (!urlStatus) return;
    urlStatus.textContent = message || "";
    urlStatus.className = "tool-status" + (state ? " tool-status-" + state : "");
  }

  var GROUPS = [
    { status: "attention", severity: "error", label: "needs attention" },
    { status: "pass", severity: "info", label: "passing" },
    { status: "info", severity: "warning", label: "for information" },
    { status: "skipped", severity: "info", label: "not applicable" }
  ];

  function render(result) {
    lastResult = result;
    if (emptyState) emptyState.hidden = true;
    if (resultsState) resultsState.hidden = false;

    var summary = result.summary;
    if (scoreNumber) scoreNumber.textContent = summary.passed + "/" + summary.applicable;
    if (bandEl) bandEl.textContent = summary.band;
    if (bandDescEl) bandDescEl.textContent = summary.bandLabel;
    if (scoreBar) scoreBar.className = "lint-score-bar lint-grade-" + summary.grade;

    if (statsEl) {
      var parts = [
        summary.applicable + " checks applied",
        summary.skipped + " not applicable",
        summary.isHtml ? "HTML input" : "text input",
        summary.words + " words"
      ];
      statsEl.innerHTML = parts.join(' <span class="lint-stat-sep">&middot;</span> ');
    }

    if (!findingsEl) return;

    var html = "";
    GROUPS.forEach(function (group) {
      var items = result.checks.filter(function (check) { return check.status === group.status; });
      if (!items.length) return;
      html += '<div class="lint-group lint-group-' + group.severity + '">';
      html += '<div class="lint-group-header"><span class="lint-group-label">' +
        escapeHtml(group.label) + " (" + items.length + ")</span></div>";
      items.forEach(function (check) {
        html += '<div class="lint-item">';
        html += '<div class="lint-item-meta">';
        html += '<span class="lint-item-rule">' + escapeHtml(check.title) + "</span>";
        html += '<span class="lint-item-line">' + escapeHtml(check.confidence) + "</span>";
        html += "</div>";
        html += '<div class="lint-item-message">' + escapeHtml(check.detail) + "</div>";
        (check.evidence || []).forEach(function (item) {
          if (!item.excerpt) return;
          html += '<div class="lint-item-excerpt">' + escapeHtml(item.excerpt) + "</div>";
        });
        html += '<div class="lint-item-message"><strong>Based on:</strong> ' + escapeHtml(check.basis) + "</div>";
        html += "</div>";
      });
      html += "</div>";
    });
    findingsEl.innerHTML = html;
  }

  function run() {
    render(core.check(readInput(), pendingOptions));
  }

  function setInput(text) {
    if (!input) return;
    input.textContent = text;
    updateCharCount();
  }

  if (runBtn) runBtn.addEventListener("click", function () {
    // A pasted document carries no response headers of its own.
    pendingOptions = {};
    run();
  });

  if (input) {
    input.addEventListener("input", updateCharCount);
    input.addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        pendingOptions = {};
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
      pendingOptions = {};
      run();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      setInput("");
      lastResult = null;
      pendingOptions = {};
      if (resultsState) resultsState.hidden = true;
      if (emptyState) emptyState.hidden = false;
      setUrlStatus("");
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      if (!lastResult || !navigator.clipboard) return;
      var lines = [
        "AI Overviews extractability report",
        lastResult.summary.passed + " of " + lastResult.summary.applicable + " checks passed (" +
          lastResult.summary.bandLabel + ")",
        "This is a count of structural checks, not a prediction of AI Overview inclusion.",
        ""
      ];
      lastResult.checks.forEach(function (check) {
        lines.push("[" + check.status + "/" + check.confidence + "] " + check.title);
        lines.push("    " + check.detail);
        lines.push("    based on: " + check.basis);
      });
      navigator.clipboard.writeText(lines.join("\n")).then(function () {
        copyBtn.textContent = "copied";
        setTimeout(function () { copyBtn.textContent = "copy"; }, 1500);
      });
    });
  }

  if (urlForm) {
    urlForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var value = urlInput ? urlInput.value.trim() : "";
      if (!value) {
        setUrlStatus("Enter a page URL to check.", "error");
        return;
      }
      setUrlStatus("Fetching the page…", "loading");
      fetch("/api/fetch-page", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: value })
      })
        .then(function (response) {
          return response.json().then(function (body) {
            if (!response.ok) throw new Error(body.error || "That page could not be fetched.");
            return body;
          });
        })
        .then(function (body) {
          if (!body.found) {
            setUrlStatus(body.error || "That page could not be fetched.", "error");
            return;
          }
          setInput(body.content);
          pendingOptions = { xRobotsTag: body.xRobotsTag || "" };
          var note = "Checked " + body.finalUrl + " (" + body.bytes + " bytes).";
          if (body.xRobotsTag) note += " X-Robots-Tag: " + body.xRobotsTag + ".";
          if (body.leftOriginalSite) {
            note += " That is a different site from the URL you entered, so the result describes the redirect target.";
          }
          setUrlStatus(note, "success");
          run();
        })
        .catch(function (error) {
          setUrlStatus(error.message || "That page could not be fetched.", "error");
        });
    });
  }

  updateCharCount();
})();
