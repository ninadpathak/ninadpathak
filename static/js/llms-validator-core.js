/*
 * llms.txt validator — rule engine.
 *
 * Pure functions only. No DOM, no network, no globals beyond the export.
 * The browser loads this as a script tag; tests/test_llms_txt_validator.py
 * loads the same file through node so the tested engine is the shipped engine.
 *
 * Validated against the llms.txt proposal v2 (llmstxt.org/index.md, Jeremy
 * Howard, retrieved 2026-08-17). The spec's ordered structure is:
 *
 *   - an optional byte-order mark (BOM)
 *   - an H1 with the name of the project or site. "This is the only required
 *     section"
 *   - a blockquote with a short summary
 *   - zero or more markdown sections of any type EXCEPT headings
 *   - zero or more H2-delimited sections containing "file lists", where each
 *     list item carries "a required markdown hyperlink [name](url), then
 *     optionally a ':' and notes about the file"
 *
 * Severity is calibrated to that text. Only a genuine violation of a stated
 * requirement is an error. Everything the spec calls optional, or that is
 * convention rather than requirement, is a warning or info, and each rule
 * records which of the two it is in `basis`.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.LlmsTxtValidatorCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var SPEC = "spec";
  var CONVENTION = "convention";

  var ERROR = "error";
  var WARNING = "warning";
  var INFO = "info";

  var BOM = "﻿";

  function isBlank(line) {
    return line.trim() === "";
  }

  function headingLevel(line) {
    var match = /^(#{1,6})(\s+|$)/.exec(line);
    return match ? match[1].length : 0;
  }

  function headingText(line) {
    return line.replace(/^#{1,6}\s*/, "").replace(/\s*#*\s*$/, "").trim();
  }

  function isListItem(line) {
    return /^\s*(?:[-*+]|\d+[.)])\s+/.test(line);
  }

  function listItemBody(line) {
    return line.replace(/^\s*(?:[-*+]|\d+[.)])\s+/, "");
  }

  function isBlockquote(line) {
    return /^\s*>/.test(line);
  }

  function isFence(line) {
    return /^\s*(?:```|~~~)/.test(line);
  }

  /*
   * Parses one file-list item body. Returns a descriptor rather than throwing so
   * the caller can attach precise findings.
   */
  function parseListItem(body) {
    // A well-formed item: [name](url) optionally followed by ": notes".
    var link = /^\[([^\]]*)\]\(([^()\s]*(?:\([^()]*\)[^()\s]*)*)\)/.exec(body.trim());
    if (link) {
      var rest = body.trim().slice(link[0].length);
      var notes = "";
      var hasNotes = false;
      var noteMatch = /^\s*:\s*(.*)$/.exec(rest);
      if (noteMatch) {
        hasNotes = true;
        notes = noteMatch[1].trim();
      }
      return {
        ok: true,
        name: link[1].trim(),
        url: link[2].trim(),
        notes: notes,
        hasNotes: hasNotes,
        trailing: noteMatch ? "" : rest.trim(),
      };
    }
    // Looks like it was meant to be a link but is not valid markdown.
    var looksLikeLink = /\[[^\]]*\]/.test(body) || /\]\s*\(/.test(body) || /\(https?:\/\//i.test(body);
    return { ok: false, looksLikeLink: looksLikeLink, raw: body.trim() };
  }

  function classifyUrl(url) {
    if (!url) return { kind: "empty" };
    if (/^(?:mailto|tel):/i.test(url)) return { kind: "nonhttp", scheme: url.split(":")[0].toLowerCase() };
    if (/^https:\/\//i.test(url)) return { kind: "absolute", secure: true };
    if (/^http:\/\//i.test(url)) return { kind: "absolute", secure: false };
    if (/^[a-z][a-z0-9+.-]*:/i.test(url)) return { kind: "nonhttp", scheme: url.split(":")[0].toLowerCase() };
    return { kind: "relative" };
  }

  /*
   * Splits the document into logical regions and records the raw facts the rules
   * then interpret. Fenced code blocks are tracked so a spec example pasted into
   * the tool is not mistaken for the document's own structure.
   */
  function parse(text) {
    var hadBom = text.charAt(0) === BOM;
    var body = hadBom ? text.slice(1) : text;
    var lines = body.split(/\r\n|\n|\r/);

    var doc = {
      hadBom: hadBom,
      lines: lines,
      h1: null,
      extraH1s: [],
      blockquoteLines: [],
      preambleLines: [],
      deepHeadingsBeforeSections: [],
      sections: [],
      trailingBlockquotes: [],
    };

    var inFence = false;
    var seenH1 = false;
    var current = null;

    for (var i = 0; i < lines.length; i += 1) {
      var line = lines[i];
      var number = i + 1;

      if (isFence(line)) {
        inFence = !inFence;
        if (current) current.rawLines.push({ number: number, line: line, fenced: true });
        continue;
      }
      if (inFence) {
        if (current) current.rawLines.push({ number: number, line: line, fenced: true });
        continue;
      }

      var level = headingLevel(line);

      if (level === 1) {
        if (!seenH1) {
          seenH1 = true;
          doc.h1 = { number: number, text: headingText(line) };
        } else {
          doc.extraH1s.push({ number: number, text: headingText(line) });
        }
        current = null;
        continue;
      }

      if (level === 2) {
        current = {
          number: number,
          name: headingText(line),
          items: [],
          nonListLines: [],
          rawLines: [],
          deepHeadings: [],
        };
        doc.sections.push(current);
        continue;
      }

      if (level >= 3) {
        if (current) current.deepHeadings.push({ number: number, text: headingText(line), level: level });
        else doc.deepHeadingsBeforeSections.push({ number: number, text: headingText(line), level: level });
        continue;
      }

      if (current) {
        current.rawLines.push({ number: number, line: line, fenced: false });
        if (isListItem(line)) {
          current.items.push({ number: number, line: line, parsed: parseListItem(listItemBody(line)) });
        } else if (!isBlank(line)) {
          current.nonListLines.push({ number: number, line: line });
        }
        continue;
      }

      // Before the first H2: blockquote summary, then free prose.
      if (isBlockquote(line)) {
        if (!seenH1) doc.trailingBlockquotes.push({ number: number, line: line, beforeH1: true });
        else doc.blockquoteLines.push({ number: number, line: line });
        continue;
      }
      if (!isBlank(line)) {
        doc.preambleLines.push({ number: number, line: line, beforeH1: !seenH1 });
      }
    }

    return doc;
  }

  function finding(rule, severity, basis, message, line, excerpt) {
    var item = { rule: rule, severity: severity, basis: basis, message: message };
    if (typeof line === "number") item.line = line;
    if (excerpt) item.excerpt = String(excerpt).slice(0, 200);
    return item;
  }

  function validate(text) {
    var findings = [];
    var input = typeof text === "string" ? text : "";

    if (input.trim() === "") {
      return {
        findings: [
          finding(
            "empty-input",
            ERROR,
            SPEC,
            "The file is empty. An llms.txt file must contain at least an H1 with the name of the project or site.",
            1
          ),
        ],
        stats: { lines: 0, sections: 0, links: 0, secureLinks: 0, errors: 1, warnings: 0, infos: 0 },
        score: 0,
        grade: "F",
        gradeDesc: "not a valid llms.txt file",
      };
    }

    var doc = parse(input);

    /* ---- H1: the only required section ---- */

    if (!doc.h1) {
      findings.push(
        finding(
          "missing-h1",
          ERROR,
          SPEC,
          "No H1 found. The spec calls an H1 with the project or site name the only required section.",
          1
        )
      );
    } else if (doc.h1.text === "") {
      findings.push(
        finding("empty-h1", ERROR, SPEC, "The H1 has no text. It must name the project or site.", doc.h1.number)
      );
    }

    doc.extraH1s.forEach(function (extra) {
      findings.push(
        finding(
          "multiple-h1",
          ERROR,
          SPEC,
          "A second H1 was found. The spec allows one H1, and uses H2 to delimit file-list sections.",
          extra.number,
          extra.text
        )
      );
    });

    var preambleBeforeH1 = doc.preambleLines.filter(function (entry) {
      return entry.beforeH1;
    });
    preambleBeforeH1.forEach(function (entry) {
      findings.push(
        finding(
          "content-before-h1",
          ERROR,
          SPEC,
          "Content appears before the H1. The spec fixes the order: optional BOM, then the H1, then the summary.",
          entry.number,
          entry.line
        )
      );
    });

    doc.trailingBlockquotes.forEach(function (entry) {
      findings.push(
        finding(
          "blockquote-before-h1",
          ERROR,
          SPEC,
          "The summary blockquote appears before the H1. The H1 must come first.",
          entry.number,
          entry.line
        )
      );
    });

    /* ---- Summary blockquote: in the ordered structure, but the spec's own
       example labels it optional, so this is a warning, never an error. ---- */

    if (doc.h1 && doc.blockquoteLines.length === 0) {
      findings.push(
        finding(
          "missing-summary",
          WARNING,
          CONVENTION,
          "No summary blockquote. The spec's structure places a short blockquote summary after the H1, and its example marks it optional. Agents use it to interpret the rest of the file.",
          doc.h1.number
        )
      );
    } else if (doc.h1 && doc.blockquoteLines.length) {
      var firstQuote = doc.blockquoteLines[0];
      var prosePreamble = doc.preambleLines.filter(function (entry) {
        return !entry.beforeH1 && entry.number < firstQuote.number;
      });
      if (prosePreamble.length) {
        findings.push(
          finding(
            "summary-not-adjacent",
            WARNING,
            SPEC,
            "The summary blockquote does not directly follow the H1. The spec orders the blockquote before any free-form detail.",
            firstQuote.number
          )
        );
      }
      var quoteText = doc.blockquoteLines
        .map(function (entry) {
          return entry.line.replace(/^\s*>\s?/, "");
        })
        .join(" ")
        .trim();
      if (quoteText === "") {
        findings.push(
          finding("empty-summary", WARNING, CONVENTION, "The summary blockquote is empty.", firstQuote.number)
        );
      }
    }

    /* ---- Headings are not allowed in the free-prose region ---- */

    doc.deepHeadingsBeforeSections.forEach(function (heading) {
      findings.push(
        finding(
          "heading-in-details",
          ERROR,
          SPEC,
          "An H" +
            heading.level +
            " appears before any H2 section. The spec allows markdown sections of any type except headings in that region, and delimits file lists with H2.",
          heading.number,
          heading.text
        )
      );
    });

    /* ---- BOM ---- */

    if (doc.hadBom) {
      findings.push(
        finding(
          "bom-present",
          INFO,
          SPEC,
          "A byte-order mark is present. The spec permits it, and it is not required.",
          1
        )
      );
    }

    /* ---- Sections and file lists ---- */

    var seenUrls = Object.create(null);
    var seenSectionNames = Object.create(null);
    var totalLinks = 0;
    var secureLinks = 0;
    var optionalSectionIndex = -1;

    doc.sections.forEach(function (section, index) {
      if (section.name === "") {
        findings.push(finding("empty-section-name", WARNING, SPEC, "An H2 heading has no text.", section.number));
      }

      var key = section.name.toLowerCase();
      if (key !== "") {
        if (seenSectionNames[key]) {
          findings.push(
            finding(
              "duplicate-section-name",
              WARNING,
              CONVENTION,
              'Section "' + section.name + '" repeats an earlier section name. Merge them so an agent sees one list per topic.',
              section.number,
              section.name
            )
          );
        }
        seenSectionNames[key] = true;
      }

      if (key === "optional") optionalSectionIndex = index;

      section.deepHeadings.forEach(function (heading) {
        findings.push(
          finding(
            "nested-heading-in-section",
            ERROR,
            SPEC,
            "An H" + heading.level + ' inside section "' + section.name + '". File-list sections are delimited by H2 only.',
            heading.number,
            heading.text
          )
        );
      });

      if (section.items.length === 0) {
        findings.push(
          finding(
            "empty-section",
            WARNING,
            SPEC,
            'Section "' + section.name + '" contains no list items. An H2 section is meant to hold a file list.',
            section.number,
            section.name
          )
        );
      }

      section.nonListLines.forEach(function (entry) {
        findings.push(
          finding(
            "non-list-content-in-section",
            WARNING,
            CONVENTION,
            "Content that is not a list item sits inside a file-list section. The spec describes these sections as holding file lists; move prose above the first H2.",
            entry.number,
            entry.line
          )
        );
      });

      section.items.forEach(function (item) {
        var parsed = item.parsed;
        if (!parsed.ok) {
          findings.push(
            finding(
              parsed.looksLikeLink ? "malformed-link" : "list-item-without-link",
              ERROR,
              SPEC,
              parsed.looksLikeLink
                ? "This list item is not a valid markdown link. The required form is [name](url), optionally followed by a colon and notes."
                : "This list item has no markdown hyperlink. Each file-list item requires [name](url).",
              item.number,
              parsed.raw
            )
          );
          return;
        }

        totalLinks += 1;

        if (parsed.name === "") {
          findings.push(
            finding("empty-link-name", ERROR, SPEC, "This link has no title. The required form is [name](url).", item.number, item.line.trim())
          );
        }

        var urlKind = classifyUrl(parsed.url);
        if (urlKind.kind === "empty") {
          findings.push(
            finding("empty-link-url", ERROR, SPEC, "This link has an empty URL.", item.number, item.line.trim())
          );
        } else if (urlKind.kind === "relative") {
          findings.push(
            finding(
              "relative-link-url",
              WARNING,
              CONVENTION,
              "This URL is relative. An agent may read the file without knowing its base, so absolute URLs are the safer form. The spec's example uses absolute URLs.",
              item.number,
              parsed.url
            )
          );
        } else if (urlKind.kind === "nonhttp") {
          findings.push(
            finding(
              "non-http-link-url",
              WARNING,
              CONVENTION,
              'This URL uses the "' + urlKind.scheme + '" scheme. File lists point at readable documents over http or https.',
              item.number,
              parsed.url
            )
          );
        } else {
          if (urlKind.secure) secureLinks += 1;
          else {
            findings.push(
              finding("insecure-link-url", WARNING, CONVENTION, "This URL uses http rather than https.", item.number, parsed.url)
            );
          }
          var urlKey = parsed.url.replace(/#.*$/, "");
          if (seenUrls[urlKey]) {
            findings.push(
              finding(
                "duplicate-link-url",
                WARNING,
                CONVENTION,
                "This URL already appears on line " + seenUrls[urlKey] + ". Duplicates spend an agent's context twice.",
                item.number,
                parsed.url
              )
            );
          } else {
            seenUrls[urlKey] = item.number;
          }
        }

        if (parsed.ok && !parsed.hasNotes) {
          findings.push(
            finding(
              "link-without-notes",
              INFO,
              SPEC,
              "This link has no notes. Notes are optional in the spec, and they are what tells an agent why the link is worth fetching.",
              item.number,
              parsed.name
            )
          );
        }

        if (parsed.hasNotes && parsed.notes === "") {
          findings.push(
            finding("empty-link-notes", WARNING, CONVENTION, "This link ends in a colon with no notes after it.", item.number, item.line.trim())
          );
        }

        if (parsed.trailing) {
          findings.push(
            finding(
              "unparsed-trailing-text",
              WARNING,
              SPEC,
              "Text follows the link without the colon the spec uses to introduce notes.",
              item.number,
              parsed.trailing
            )
          );
        }
      });
    });

    if (optionalSectionIndex !== -1 && optionalSectionIndex !== doc.sections.length - 1) {
      findings.push(
        finding(
          "optional-section-not-last",
          WARNING,
          CONVENTION,
          'The "Optional" section is not last. By convention it holds secondary links an agent can skip, so trailing placement matches how it is read.',
          doc.sections[optionalSectionIndex].number
        )
      );
    }

    if (doc.h1 && doc.sections.length === 0) {
      findings.push(
        finding(
          "no-sections",
          WARNING,
          SPEC,
          "No H2 file-list sections. The spec allows zero, so this is valid, but a file with no links gives an agent nothing to fetch.",
          doc.h1.number
        )
      );
    }

    /* ---- Score ---- */

    var errors = 0;
    var warnings = 0;
    var infos = 0;
    findings.forEach(function (item) {
      if (item.severity === ERROR) errors += 1;
      else if (item.severity === WARNING) warnings += 1;
      else infos += 1;
    });

    var score = 100 - errors * 12 - warnings * 4;
    if (score < 0) score = 0;
    // The H1 is the spec's only hard requirement. Without it the file is not an
    // llms.txt file, whatever else it gets right.
    if (!doc.h1) score = Math.min(score, 40);

    var grade = "F";
    var gradeDesc = "does not follow the spec";
    if (score >= 90) {
      grade = "A";
      gradeDesc = "follows the spec";
    } else if (score >= 80) {
      grade = "B";
      gradeDesc = "valid, with room to tighten";
    } else if (score >= 70) {
      grade = "C";
      gradeDesc = "valid, several issues";
    } else if (score >= 60) {
      grade = "D";
      gradeDesc = "significant issues";
    }

    var order = { error: 0, warning: 1, info: 2 };
    findings.sort(function (a, b) {
      if (order[a.severity] !== order[b.severity]) return order[a.severity] - order[b.severity];
      return (a.line || 0) - (b.line || 0);
    });

    return {
      findings: findings,
      stats: {
        lines: doc.lines.length,
        sections: doc.sections.length,
        links: totalLinks,
        secureLinks: secureLinks,
        errors: errors,
        warnings: warnings,
        infos: infos,
      },
      score: score,
      grade: grade,
      gradeDesc: gradeDesc,
      title: doc.h1 ? doc.h1.text : "",
    };
  }

  return { validate: validate, parse: parse, SPEC_VERSION: "v2" };
});
