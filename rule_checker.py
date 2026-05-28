#!/usr/bin/env python3
"""
Corpus-wide writing rule checker for ninadpathak.com blog posts.

Usage:
  python3 rule_checker.py                    # check all posts
  python3 rule_checker.py path/to/post.md   # check one post
  python3 rule_checker.py --summary          # summary counts only

Rules enforced:
  ERROR  - em dashes, contrastive parallelism, horizontal lines in prose,
           forbidden jargon (leverage/synergy/unlock)
  WARNING - banned sentence starters, double dashes, prose semicolons
  INFO   - missing slug in frontmatter, missing visual embed
"""

import re
import sys
import pathlib
import frontmatter as fm_lib

ROOT = pathlib.Path(__file__).parent

BANNED_STARTERS = {"in", "this", "by", "finally", "most", "ever"}

CONTRASTIVE_PATTERNS = [
    (r'\bunlike\b', '"Unlike X, Y" — contrastive parallelism'),
    (r'\bwhereas\b', '"whereas" — contrastive parallelism'),
    (r'\bon the other hand\b', '"on the other hand" — contrastive parallelism'),
    # "while X does/is/has Y" (not temporal "while the loop runs")
    (r'\bwhile\b[^.]{0,60}\b(?:does|does not|is|is not|has|can|cannot|will|would|should)\b',
     '"while X does/is Y" — likely contrastive parallelism'),
]

FORBIDDEN_WORDS = {
    "leverage": "use / rely on",
    "leverages": "uses / relies on",
    "leveraging": "using / relying on",
    "synergy": "remove or be specific",
    "synergies": "remove or be specific",
    "unlock": "enable / reveal",
    "unlocks": "enables / reveals",
}

def get_prose(text):
    """Strip frontmatter, code fences, inline code, HTML embeds, HTML tags, comments."""
    parts = text.split('---', 2)
    body = parts[2] if len(parts) > 2 else text
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    body = re.sub(r'```.*?```', '', body, flags=re.S)
    body = re.sub(r'`[^`]+`', '', body)
    body = re.sub(r'<div class="visual-wrapper">.*?</div>\s*</div>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', '', body)
    return body


def check_post(path):
    path = pathlib.Path(path)
    text = path.read_text(encoding='utf-8')
    prose = get_prose(text)
    issues = []  # (severity, rule, line_hint, message)

    # ── 1. Em dashes ───────────────────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if '—' in line:
            snippet = line.strip()[:90]
            issues.append(('error', 'em-dash', i, f'Em dash: {snippet}'))

    # ── 2. Double dashes in prose ──────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if re.search(r'(?<!\-)\-\-(?!\-)', line):
            issues.append(('warning', 'double-dash', i, f'Double dash: {line.strip()[:90]}'))

    # ── 3. Prose semicolons ────────────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if re.search(r'\w;', line):
            issues.append(('warning', 'semicolon', i, f'Semicolon in prose: {line.strip()[:90]}'))

    # ── 4. Contrastive parallelism ─────────────────────────────────────
    for pat, label in CONTRASTIVE_PATTERNS:
        for m in re.finditer(pat, prose, re.I):
            start = max(0, m.start() - 20)
            snippet = prose[start:m.start() + 80].replace('\n', ' ').strip()
            issues.append(('error', 'contrastive', None, f'{label}: "...{snippet}..."'))

    # ── 5. Horizontal lines in prose body ─────────────────────────────
    parts = text.split('---', 2)
    if len(parts) > 2:
        body_no_code = re.sub(r'```.*?```', '', parts[2], flags=re.S)
        for i, line in enumerate(body_no_code.splitlines(), 1):
            if re.match(r'^---+\s*$', line):
                issues.append(('error', 'hr', i, f'Horizontal line (---) in prose body'))

    # ── 6. Banned sentence starters ───────────────────────────────────
    for sentence in re.split(r'(?<=[.!?])\s+', prose):
        s = sentence.strip()
        if not s or s[0] in '#-*>|':
            continue
        m = re.match(r'[*_"\']*([A-Za-z]+)', s)
        if m and m.group(1).lower() in BANNED_STARTERS:
            snippet = s[:80]
            issues.append(('warning', 'banned-starter',
                            None, f'Sentence starts with "{m.group(1)}": {snippet}'))

    # ── 7. Forbidden jargon words ──────────────────────────────────────
    for word, suggestion in FORBIDDEN_WORDS.items():
        for m in re.finditer(r'\b' + word + r'\b', prose, re.I):
            start = max(0, m.start() - 20)
            snippet = prose[start:m.start() + 60].replace('\n', ' ').strip()
            issues.append(('error', 'jargon', None,
                            f'Forbidden word "{m.group(0)}" (use: {suggestion}): ...{snippet}...'))

    # ── 8. Frontmatter: missing explicit slug ──────────────────────────
    try:
        post = fm_lib.load(path)
        if not post.get('slug'):
            issues.append(('warning', 'no-slug', None,
                            'No explicit slug in frontmatter — URL will use filename'))
        if not post.get('description'):
            issues.append(('warning', 'no-desc', None, 'No description in frontmatter'))
    except Exception:
        pass

    # ── 9. Missing visual embed ────────────────────────────────────────
    if 'static/visuals' not in text:
        issues.append(('info', 'no-visual', None, 'No visual embed found'))

    return issues


def check_all(paths, summary_only=False):
    counts = {'error': 0, 'warning': 0, 'info': 0}
    post_counts = {}

    for path in sorted(paths):
        issues = check_post(path)
        if not issues:
            if not summary_only:
                print(f'  OK  {path.name}')
            continue

        errors   = [i for i in issues if i[0] == 'error']
        warnings = [i for i in issues if i[0] == 'warning']
        infos    = [i for i in issues if i[0] == 'info']

        counts['error']   += len(errors)
        counts['warning'] += len(warnings)
        counts['info']    += len(infos)
        post_counts[path.name] = len(issues)

        if summary_only:
            if errors or warnings:
                print(f'  {path.name}: {len(errors)}E {len(warnings)}W {len(infos)}I')
            continue

        print(f'\n── {path.name} ──')
        for sev, rule, line, msg in errors:
            loc = f'L{line} ' if line else ''
            print(f'  ERROR   [{rule}] {loc}{msg}')
        for sev, rule, line, msg in warnings:
            loc = f'L{line} ' if line else ''
            print(f'  WARN    [{rule}] {loc}{msg}')
        for sev, rule, line, msg in infos:
            print(f'  INFO    [{rule}] {msg}')

    return counts, post_counts


if __name__ == '__main__':
    args = sys.argv[1:]
    summary_only = '--summary' in args
    args = [a for a in args if a != '--summary']

    if args:
        paths = [pathlib.Path(a) for a in args]
    else:
        paths = list((ROOT / 'content/posts').glob('*.md'))

    counts, post_counts = check_all(paths, summary_only=summary_only)

    print(f'\n{"─"*60}')
    print(f'TOTAL: {counts["error"]} errors, {counts["warning"]} warnings, {counts["info"]} info')
    if post_counts:
        worst = sorted(post_counts.items(), key=lambda x: -x[1])[:5]
        print(f'Top offenders: {", ".join(n for n,_ in worst)}')
