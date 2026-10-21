// Brand tokens: load, check WCAG contrast, compare with the site palette, and emit CSS.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
export const TOOL_DIR = path.resolve(here, '..');
export const REPO_DIR = path.resolve(TOOL_DIR, '..', '..');

export function loadTokens() {
  return JSON.parse(readFileSync(path.join(TOOL_DIR, 'brand.tokens.json'), 'utf8'));
}

function luminance(hex) {
  const n = parseInt(hex.slice(1), 16);
  const channel = (v) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * channel((n >> 16) & 255) + 0.7152 * channel((n >> 8) & 255) + 0.0722 * channel(n & 255);
}

export function contrastRatio(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

// Every pair the guideline promises, in both schemes. Returns rows; `ok` is false on a breach.
export function contrastReport(tokens) {
  const rows = [];
  for (const scheme of ['light', 'dark']) {
    const palette = tokens.color[scheme];
    for (const rule of tokens.contrast) {
      for (const bg of rule.bg) {
        const ratio = contrastRatio(palette[rule.fg].value, palette[bg].value);
        rows.push({ scheme, fg: rule.fg, bg, ratio: Math.round(ratio * 100) / 100, min: rule.min, use: rule.use, ok: ratio >= rule.min });
      }
    }
  }
  return rows;
}

// Compare image tokens with the live site tokens in static/css/main.css.
export function siteDrift(tokens, mainCssPath = path.join(REPO_DIR, 'static/css/main.css')) {
  const css = readFileSync(mainCssPath, 'utf8');
  const block = (selector) => {
    const match = css.match(new RegExp(selector.replace(/[[\]"=]/g, '\\$&') + '\\s*\\{([\\s\\S]*?)\\}'));
    return match ? Object.fromEntries([...match[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)].map((m) => [m[1], m[2].trim().toLowerCase()])) : {};
  };
  const light = block(':root');
  const site = { light, dark: { ...light, ...block('[data-theme="dark"]') } };
  const drift = [];
  for (const scheme of ['light', 'dark']) {
    for (const [name, token] of Object.entries(tokens.color[scheme])) {
      const siteName = token.site ?? tokens.color.light[name].site;
      if (!siteName || (scheme === 'dark' && token.site === null)) continue;
      const live = site[scheme][siteName];
      if (live && live !== token.value.toLowerCase()) drift.push({ scheme, token: name, site: siteName, image: token.value, live });
    }
  }
  return drift;
}

const vars = (palette, indent) =>
  Object.entries(palette).map(([name, t]) => `${indent}--np-${name}: ${t.value};`).join('\n');

// CSS for a plate: brand variables per scheme, then the Pele variables mapped onto them.
export function themeCss(tokens) {
  const { light, dark } = tokens.color;
  const t = tokens.type;
  return `.np-plate {
${vars(light, '  ')}
  --np-sans: '${t.sans}', ${t.sansFallback};
  --np-mono: '${t.mono}', ${t.monoFallback};
  --pele-bg: var(--np-canvas);
  --pele-fg: var(--np-ink);
  --pele-muted: var(--np-muted);
  --pele-line: var(--np-line);
  --pele-surface: var(--np-surface);
  --pele-surface-alt: var(--np-surface-2);
  --pele-border: var(--np-rule);
  --pele-accent: var(--np-accent);
  --pele-critical: var(--np-danger);
  --pele-error: var(--np-danger);
  --pele-font: var(--np-sans);
  --pele-font-mono: var(--np-mono);
  --pele-radius: ${tokens.radius.node}px;
  --pele-title-weight: 600;
  --pele-heading-weight: 600;
  --pele-bold-weight: 700;
  --pele-series-1: var(--np-accent);
  --pele-series-2: var(--np-ink-2);
  --pele-series-3: var(--np-muted);
  --pele-series-4: var(--np-rule);
  --pele-series-5: var(--np-danger);
  --pele-series-6: var(--np-success);
  --pele-series-7: var(--np-line);
  --pele-series-8: var(--np-hairline);
}
@media (prefers-color-scheme: dark) {
  .np-plate:not(.np-light) {
${vars(dark, '    ')}
  }
}
.np-plate.np-dark, [data-theme="dark"] .np-plate {
${vars(dark, '  ')}
}
[data-theme="light"] .np-plate:not(.np-dark) {
${vars(light, '  ')}
}
`;
}
