/*
 * Minimal DOM shim for exercising the tool pages' client logic without a browser.
 *
 * WHY THIS EXISTS, AND WHAT IT IS NOT
 *
 * The rule engines have unit tests, but they load through require(), which takes the
 * CommonJS branch of each engine's UMD wrapper. The browser takes the other branch and
 * assigns a global. Nothing tested that branch, nor that the wiring script finds the
 * global, nor that the element ids it queries exist in the built page. A tool could pass
 * every unit test and be dead on the page.
 *
 * This runs the shipped wiring script against the shipped engine, in a sandbox where
 * `module` is deliberately absent so the UMD wrapper takes the browser path, with a DOM
 * built from the ids actually parsed out of the built HTML.
 *
 * It is NOT a browser. It does not lay out, style, or paint, it does not run main.js, and
 * it cannot catch anything that depends on real browser behaviour: focus management,
 * clipboard permissions, contenteditable quirks, CSS. What it does catch is the seam that
 * has actually broken in this repo: a renamed id, a renamed global, a script that stopped
 * loading, an engine whose output shape changed, and a wiring script that references an
 * element the template no longer has.
 *
 * Protocol. Reads one JSON object on stdin:
 *   { ids: [...], classes: [...], scripts: [absolute paths in load order],
 *     text: {id: "content"},      set textContent/innerText before running
 *     values: {id: "value"},      set .value before running
 *     click: "buttonId",          dispatch a click
 *     fetch: {status, body}       canned response for the single fetch call, optional
 *     collect: [ids]              elements whose state to return }
 * Writes one JSON object on stdout:
 *   { elements: {id: {text, html, className, hidden}}, fetchCalls: [...], errors: [...] }
 */
"use strict";

const fs = require("fs");
const vm = require("vm");

function readStdin() {
  return new Promise((resolve) => {
    let buf = "";
    process.stdin.on("data", (c) => { buf += c; });
    process.stdin.on("end", () => resolve(JSON.parse(buf || "{}")));
  });
}

function makeElement(id, doc) {
  const el = {
    id: id,
    tagName: "DIV",
    className: "",
    hidden: false,
    value: "",
    checked: false,
    disabled: false,
    dataset: {},
    style: {},
    _text: "",
    _html: "",
    _listeners: {},
    children: [],
    parentNode: null,
  };

  Object.defineProperty(el, "textContent", {
    get() { return el._text; },
    set(v) { el._text = String(v); el._html = ""; },
  });
  // The wiring scripts read innerText from contenteditable panes.
  Object.defineProperty(el, "innerText", {
    get() { return el._text; },
    set(v) { el._text = String(v); el._html = ""; },
  });
  Object.defineProperty(el, "innerHTML", {
    get() { return el._html; },
    set(v) { el._html = String(v); },
  });

  el.addEventListener = function (type, fn) {
    (el._listeners[type] = el._listeners[type] || []).push(fn);
  };
  el.removeEventListener = function (type, fn) {
    const list = el._listeners[type] || [];
    const at = list.indexOf(fn);
    if (at !== -1) list.splice(at, 1);
  };
  el.dispatchEvent = function (event) {
    (el._listeners[event.type] || []).forEach((fn) => fn.call(el, event));
    return true;
  };
  el.click = function () {
    el.dispatchEvent({ type: "click", target: el, preventDefault() {}, stopPropagation() {} });
  };
  el.focus = function () {};
  el.blur = function () {};
  el.remove = function () {
    if (el.parentNode) {
      const at = el.parentNode.children.indexOf(el);
      if (at !== -1) el.parentNode.children.splice(at, 1);
    }
  };
  el.appendChild = function (child) {
    child.parentNode = el;
    el.children.push(child);
    return child;
  };
  el.setAttribute = function (name, v) {
    if (name === "class") el.className = String(v);
    else if (name === "id") el.id = String(v);
    else el[name] = v;
  };
  el.getAttribute = function (name) {
    if (name === "class") return el.className;
    if (name === "id") return el.id;
    return el[name] === undefined ? null : el[name];
  };
  el.hasAttribute = function (name) { return el.getAttribute(name) !== null; };

  // Selector support is deliberately minimal: class, tag, and #id only. Anything more
  // would be a second implementation of a CSS engine, which would be its own bug surface.
  function matches(node, selector) {
    selector = String(selector).trim();
    if (selector.startsWith(".")) {
      return (" " + node.className + " ").indexOf(" " + selector.slice(1) + " ") !== -1;
    }
    if (selector.startsWith("#")) return node.id === selector.slice(1);
    return node.tagName.toLowerCase() === selector.toLowerCase();
  }
  el.matches = function (selector) { return matches(el, selector); };
  el.closest = function (selector) {
    let node = el;
    while (node) {
      if (matches(node, selector)) return node;
      node = node.parentNode;
    }
    return null;
  };
  el.querySelector = function (selector) {
    for (const child of el.children) {
      if (matches(child, selector)) return child;
      const deeper = child.querySelector && child.querySelector(selector);
      if (deeper) return deeper;
    }
    return null;
  };
  el.querySelectorAll = function (selector) {
    const found = [];
    for (const child of el.children) {
      if (matches(child, selector)) found.push(child);
      if (child.querySelectorAll) found.push(...child.querySelectorAll(selector));
    }
    return found;
  };
  return el;
}

async function main() {
  const spec = await readStdin();
  const errors = [];
  const fetchCalls = [];

  const elements = {};
  const doc = {
    _listeners: {},
    getElementById(id) { return elements[id] || null; },
    createElement(tag) {
      const el = makeElement("", doc);
      el.tagName = String(tag).toUpperCase();
      return el;
    },
    addEventListener(type, fn) { (doc._listeners[type] = doc._listeners[type] || []).push(fn); },
    // Class selectors resolve against the classes actually present in the built page, so a
    // query for an element the template has succeeds and a query for one it does not have
    // returns null. Returning a stub for everything would mask exactly the break these
    // tests look for. linter.js queries .linter-results-container this way.
    querySelector(selector) {
      const sel = String(selector).trim();
      if (sel.startsWith("#")) return elements[sel.slice(1)] || null;
      if (sel.startsWith(".") && (spec.classes || []).indexOf(sel.slice(1)) !== -1) {
        const key = "__class__" + sel.slice(1);
        if (!elements[key]) elements[key] = makeElement(key, doc);
        return elements[key];
      }
      return null;
    },
    querySelectorAll(selector) {
      const one = doc.querySelector(selector);
      return one ? [one] : [];
    },
    // Used by the paste handlers to insert plain text. Not exercised here, but it must
    // exist or the handler registration throws.
    execCommand(name, _show, value) {
      if (name === "insertText" && doc._focused) doc._focused._text += String(value);
      return true;
    },
  };
  doc.body = makeElement("__body__", doc);
  doc.documentElement = makeElement("__html__", doc);

  (spec.ids || []).forEach((id) => { elements[id] = makeElement(id, doc); });

  const sandbox = {
    console: { log() {}, warn() {}, error() {} },
    document: doc,
    navigator: { clipboard: { writeText() { return Promise.resolve(); } }, userAgent: "harness" },
    setTimeout: (fn) => { void fn; return 0 },   // never fire: keeps the run deterministic
    clearTimeout() {},
    JSON: JSON,
    Math: Math,
    Date: Date,
    RegExp: RegExp,
    Promise: Promise,
    Error: Error,
    encodeURIComponent: encodeURIComponent,
    decodeURIComponent: decodeURIComponent,
    URL: URL,
    TextEncoder: TextEncoder,
    fetch(url, opts) {
      fetchCalls.push({ url: String(url), method: (opts && opts.method) || "GET",
                        body: opts && opts.body ? String(opts.body) : null });
      // `fetch` may be a single canned response or a list, one per call in order. The
      // generator makes two calls with different shapes, so a single response cannot
      // exercise it honestly.
      const queue = Array.isArray(spec.fetch) ? spec.fetch : [spec.fetch];
      const at = Math.min(fetchCalls.length - 1, queue.length - 1);
      const canned = queue[at] || { status: 200, body: {} };
      return Promise.resolve({
        ok: canned.status >= 200 && canned.status < 300,
        status: canned.status,
        json: () => Promise.resolve(canned.body),
        text: () => Promise.resolve(JSON.stringify(canned.body)),
      });
    },
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  sandbox.globalThis = sandbox;
  // `module` is intentionally NOT defined. Every engine ships a UMD wrapper that assigns a
  // global when module is absent, which is the branch the browser takes and the branch the
  // require()-based unit tests never reach.

  const context = vm.createContext(sandbox);

  for (const scriptPath of spec.scripts || []) {
    let source;
    try {
      source = fs.readFileSync(scriptPath, "utf8");
    } catch (exc) {
      errors.push("cannot read " + scriptPath + ": " + exc.message);
      continue;
    }
    try {
      vm.runInContext(source, context, { filename: scriptPath, timeout: 10000 });
    } catch (exc) {
      errors.push("throw while loading " + scriptPath + ": " + exc.message);
    }
  }

  // A browser fires this once the document is parsed. linter.js registers every handler
  // inside it, so without this the page loads and nothing is wired — which is exactly the
  // silent-break class these tests exist to catch.
  (doc._listeners.DOMContentLoaded || []).forEach((fn) => {
    try {
      fn({ type: "DOMContentLoaded" });
    } catch (exc) {
      errors.push("throw in DOMContentLoaded: " + exc.message);
    }
  });

  Object.entries(spec.text || {}).forEach(([id, value]) => {
    if (elements[id]) elements[id].textContent = value;
    else errors.push("no element " + id + " to set text on");
  });
  Object.entries(spec.values || {}).forEach(([id, value]) => {
    if (elements[id]) elements[id].value = value;
    else errors.push("no element " + id + " to set value on");
  });

  if (spec.click) {
    const target = elements[spec.click];
    if (!target) errors.push("no element " + spec.click + " to click");
    else {
      try {
        target.click();
      } catch (exc) {
        errors.push("throw on click " + spec.click + ": " + exc.message);
      }
    }
  }

  if (spec.submit) {
    const form = elements[spec.submit];
    if (!form) errors.push("no form " + spec.submit + " to submit");
    else {
      try {
        form.dispatchEvent({ type: "submit", target: form,
                             preventDefault() {}, stopPropagation() {} });
      } catch (exc) {
        errors.push("throw on submit " + spec.submit + ": " + exc.message);
      }
    }
  }

  // Let any promise chain the click started settle before reading the DOM.
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));

  const collected = {};
  (spec.collect || Object.keys(elements)).forEach((id) => {
    const el = elements[id];
    if (!el) return;
    collected[id] = { text: el._text, html: el._html, className: el.className,
                      hidden: el.hidden, value: el.value };
  });

  const globals = Object.keys(sandbox).filter((k) => /Core$/.test(k));
  process.stdout.write(JSON.stringify({ elements: collected, fetchCalls, errors, globals }));
}

main().catch((exc) => {
  process.stdout.write(JSON.stringify({ elements: {}, fetchCalls: [],
                                        errors: ["harness failure: " + exc.message] }));
});
