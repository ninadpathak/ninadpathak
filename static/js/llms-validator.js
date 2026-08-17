/*
 * llms.txt validator — browser wiring.
 *
 * All rules live in llms-validator-core.js. This file only moves text between
 * the DOM and that engine, and renders findings using the existing linter.css
 * vocabulary. No CSS is added anywhere.
 *
 * Privacy contract, enforced by construction:
 *   - The paste path calls the engine directly. Pasted text never leaves the
 *     page: there is no fetch, no beacon, no storage on that path.
 *   - The domain path posts only a domain string to /api/fetch-llms-txt, which
 *     needs a server hop because a browser cannot read another origin's file.
 */
(function () {
  "use strict";

  var core = window.LlmsTxtValidatorCore;
  if (!core) return;

  var input = document.getElementById("validatorInput");
  var runBtn = document.getElementById("validateBtn");
  var clearBtn = document.getElementById("clearValidator");
  var copyBtn = document.getElementById("copyValidatorResults");
  var sampleBtn = document.getElementById("loadValidatorSample");
  var charCount = document.getElementById("validatorCharCount");

  var emptyState = document.getElementById("validatorEmpty");
  var resultsState = document.getElementById("validatorResults");
  var scoreBar = document.getElementById("validatorScoreBar");
  var scoreNumber = document.getElementById("validatorScore");
  var gradeEl = document.getElementById("validatorGrade");
  var gradeDescEl = document.getElementById("validatorGradeDesc");
  var statsEl = document.getElementById("validatorStats");
  var findingsEl = document.getElementById("validatorFindings");

  var domainForm = document.getElementById("validatorDomainForm");
  var domainInput = document.getElementById("validatorDomain");
  var domainStatus = document.getElementById("validatorDomainStatus");

  var lastResult = null;

  var SAMPLE = [
    "# Example Project",
    "",
    "> A short summary an agent reads first, so the rest of the file makes sense.",
    "",
    "Notes that do not belong under a heading go here.",
    "",
    "## Docs",
    "",
    "- [Quickstart](https://example.com/docs/quickstart.md): First working request in about five minutes",
    "- [API reference](https://example.com/docs/api.md): Every endpoint, parameter, and error code",
    "",
    "## Optional",
    "",
    "- [Changelog](https://example.com/changelog.md): Release history",
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
    var lines = text.trim() === "" ? 0 : text.split(/\r\n|\n|\r/).length;
    charCount.textContent = lines + (lines === 1 ? " line" : " lines");
  }

  function setDomainStatus(message, state) {
    if (!domainStatus) return;
    domainStatus.textContent = message || "";
    domainStatus.className = "tool-status" + (state ? " tool-status-" + state : "");
  }

  function severityLabel(severity) {
    if (severity === "error") return "spec violations";
    if (severity === "warning") return "warnings";
    return "notes";
  }

  function render(result) {
    lastResult = result;
    if (emptyState) emptyState.hidden = true;
    if (resultsState) resultsState.hidden = false;

    if (scoreNumber) scoreNumber.textContent = result.score;
    if (gradeEl) gradeEl.textContent = result.grade;
    if (gradeDescEl) gradeDescEl.textContent = result.gradeDesc;
    if (scoreBar) scoreBar.className = "lint-score-bar lint-grade-" + result.grade.toLowerCase();

    if (statsEl) {
      var parts = [
        result.stats.sections + (result.stats.sections === 1 ? " section" : " sections"),
        result.stats.links + (result.stats.links === 1 ? " link" : " links"),
        result.stats.errors + " errors",
        result.stats.warnings + " warnings"
      ];
      statsEl.innerHTML = parts.join(' <span class="lint-stat-sep">&middot;</span> ');
    }

    if (!findingsEl) return;

    var groups = [
      { severity: "error", items: [] },
      { severity: "warning", items: [] },
      { severity: "info", items: [] }
    ];
    result.findings.forEach(function (item) {
      for (var i = 0; i < groups.length; i += 1) {
        if (groups[i].severity === item.severity) groups[i].items.push(item);
      }
    });

    var html = "";
    groups.forEach(function (group) {
      if (!group.items.length) return;
      html += '<div class="lint-group lint-group-' + group.severity + '">';
      html += '<div class="lint-group-header"><span class="lint-group-label">' +
        escapeHtml(severityLabel(group.severity)) + " (" + group.items.length + ")</span></div>";
      group.items.forEach(function (item) {
        html += '<div class="lint-item">';
        html += '<div class="lint-item-meta">';
        html += '<span class="lint-item-rule">' + escapeHtml(item.rule) + "</span>";
        if (typeof item.line === "number") {
          html += '<span class="lint-item-line">line ' + item.line + "</span>";
        }
        html += "</div>";
        if (item.excerpt) {
          html += '<div class="lint-item-excerpt">' + escapeHtml(item.excerpt) + "</div>";
        }
        html += '<div class="lint-item-message">' + escapeHtml(item.message) + "</div>";
        html += "</div>";
      });
      html += "</div>";
    });

    if (!html) {
      html = '<div class="lint-group lint-group-info">' +
        '<div class="lint-group-header"><span class="lint-group-label">no findings</span></div>' +
        '<div class="lint-item"><div class="lint-item-message">' +
        "This file follows the llms.txt spec. Nothing to change." +
        "</div></div></div>";
    }
    findingsEl.innerHTML = html;
  }

  function run() {
    render(core.validate(readInput()));
  }

  function setInput(text) {
    if (!input) return;
    input.textContent = text;
    updateCharCount();
  }

  if (runBtn) runBtn.addEventListener("click", run);

  if (input) {
    input.addEventListener("input", updateCharCount);
    input.addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        run();
      }
    });
    // Keep pasted content as plain text so markdown structure survives.
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
      var lines = ["llms.txt validation report", "score " + lastResult.score + " (" + lastResult.grade + ")", ""];
      lastResult.findings.forEach(function (item) {
        lines.push(
          "[" + item.severity + "] " + item.rule +
          (typeof item.line === "number" ? " (line " + item.line + ")" : "") +
          " — " + item.message
        );
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
      setDomainStatus("Fetching llms.txt…", "loading");
      fetch("/api/fetch-llms-txt", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: value })
      })
        .then(function (response) {
          return response.json().then(function (body) {
            if (!response.ok) throw new Error(body.error || "The file could not be fetched.");
            return body;
          });
        })
        .then(function (body) {
          if (!body.found) {
            setDomainStatus(body.error || "No llms.txt found at that domain.", "error");
            return;
          }
          setInput(body.content);
          if (body.servedAsHtml) {
            setDomainStatus(
              body.finalUrl + " returned HTML, not a markdown file. The host is most likely serving a page " +
              "instead of llms.txt, which an agent cannot use.",
              "error"
            );
          } else {
            var note = "Loaded " + body.finalUrl + " (" + body.bytes + " bytes, content-type " +
              (body.contentType || "not set") + ").";
            if (body.leftOriginalSite) {
              note += " That is a different site from the domain you entered, so the file below belongs to the redirect target.";
            }
            setDomainStatus(note, "success");
          }
          run();
        })
        .catch(function (error) {
          setDomainStatus(error.message || "The file could not be fetched.", "error");
        });
    });
  }

  updateCharCount();
})();
