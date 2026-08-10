#!/usr/bin/env python3
"""
Corpus-wide writing rule checker for ninadpathak.com blog posts.

Usage:
  python3 rule_checker.py                    # check all posts
  python3 rule_checker.py path/to/post.md   # check one post
  python3 rule_checker.py --summary          # summary counts only

Rules enforced:
  ERROR  - paragraphs over two sentences, em dashes, contrastive parallelism,
           horizontal lines in prose, forbidden jargon (leverage/synergy/unlock)
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

COMMON_ABBREVIATIONS = (
    "e.g.", "i.e.", "etc.", "vs.", "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.",
    "Sr.", "Jr.", "U.S.", "U.K."
)


def split_sentences(paragraph):
    """Split a paragraph at likely sentence boundaries without changing its text."""
    masked = paragraph
    for abbreviation in COMMON_ABBREVIATIONS:
        masked = masked.replace(abbreviation, abbreviation.replace('.', '\uE000'))

    boundaries = []
    for match in re.finditer(r'\s+', masked):
        before = masked[:match.start()].rstrip()
        after = masked[match.end():]
        if (
            re.search(r'[.!?]["”’\')\]]*$', before)
            and re.match(r'(?:[*_"“‘(\[])*[A-Z0-9]', after)
        ):
            boundaries.append((match.start(), match.end()))

    if not boundaries:
        return [paragraph.strip()] if paragraph.strip() else []

    sentences = []
    start = 0
    for boundary_start, boundary_end in boundaries:
        sentence = paragraph[start:boundary_start].strip()
        if sentence:
            sentences.append(sentence)
        start = boundary_end
    final = paragraph[start:].strip()
    if final:
        sentences.append(final)
    return sentences


def count_sentences(paragraph):
    """Count prose sentences while avoiding common abbreviation and link false positives."""
    return len(split_sentences(paragraph))


def format_two_sentence_paragraphs(body):
    """Split prose paragraphs into groups of at most two sentences."""
    output = []
    paragraph = []
    in_fence = False
    in_comment = False
    html_depth = 0

    def flush():
        nonlocal paragraph
        if not paragraph:
            return
        text = ' '.join(line.strip() for line in paragraph)
        sentences = split_sentences(text)
        output.append('\n\n'.join(
            ' '.join(sentences[index:index + 2])
            for index in range(0, len(sentences), 2)
        ))
        paragraph = []

    for line in body.splitlines():
        stripped = line.strip()

        if stripped.startswith(('```', '~~~')):
            flush()
            output.append(line)
            in_fence = not in_fence
            continue
        if in_fence:
            output.append(line)
            continue

        if in_comment:
            output.append(line)
            if '-->' in stripped:
                in_comment = False
            continue
        if '<!--' in stripped:
            flush()
            output.append(line)
            if '-->' not in stripped:
                in_comment = True
            continue

        if html_depth:
            output.append(line)
            html_depth += len(re.findall(r'<div\b', stripped, re.I))
            html_depth -= len(re.findall(r'</div>', stripped, re.I))
            continue
        if re.match(r'^<div\b', stripped, re.I):
            flush()
            output.append(line)
            html_depth = (
                len(re.findall(r'<div\b', stripped, re.I))
                - len(re.findall(r'</div>', stripped, re.I))
            )
            continue

        is_markdown_block = (
            not stripped
            or re.match(r'^(#{1,6}\s|>|[-+*]\s|\d+[.)]\s|\|)', stripped)
            or re.match(r'^\s{2,}\S', line)
            or re.match(r'^<[^>]+>', stripped)
        )
        if is_markdown_block:
            flush()
            output.append(line)
            continue

        paragraph.append(line)

    flush()
    result = '\n'.join(output)
    if body.endswith('\n'):
        result += '\n'
    return result


def paragraph_sentence_violations(body):
    """Return prose paragraphs containing more than two sentences.

    Markdown headings, lists, tables, blockquotes, fenced code, comments, and raw HTML
    blocks are intentionally excluded.
    """
    violations = []
    paragraph = []
    paragraph_start = None
    in_fence = False
    in_comment = False
    html_depth = 0

    def flush():
        nonlocal paragraph, paragraph_start
        if paragraph:
            text = ' '.join(line.strip() for line in paragraph)
            sentence_count = count_sentences(text)
            if sentence_count > 2:
                violations.append((paragraph_start, sentence_count, text[:120]))
        paragraph = []
        paragraph_start = None

    for line_number, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()

        if stripped.startswith(('```', '~~~')):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if in_comment:
            if '-->' in stripped:
                in_comment = False
            continue
        if '<!--' in stripped:
            flush()
            if '-->' not in stripped:
                in_comment = True
            continue

        if html_depth:
            html_depth += len(re.findall(r'<div\b', stripped, re.I))
            html_depth -= len(re.findall(r'</div>', stripped, re.I))
            continue
        if re.match(r'^<div\b', stripped, re.I):
            flush()
            html_depth = (
                len(re.findall(r'<div\b', stripped, re.I))
                - len(re.findall(r'</div>', stripped, re.I))
            )
            continue

        is_markdown_block = (
            not stripped
            or re.match(r'^(#{1,6}\s|>|[-+*]\s|\d+[.)]\s|\|)', stripped)
            or re.match(r'^\s{2,}\S', line)
            or re.match(r'^<[^>]+>', stripped)
        )
        if is_markdown_block:
            flush()
            continue

        if paragraph_start is None:
            paragraph_start = line_number
        paragraph.append(line)

    flush()
    return violations


def first_person_count(body):
    """Count first-person signals after removing code and raw HTML."""
    prose = re.sub(r'```.*?```', '', body, flags=re.S)
    prose = re.sub(r'`[^`]+`', '', prose)
    prose = re.sub(r'<[^>]+>', '', prose)
    return len(re.findall(
        r"\b(?:I|I'm|I've|I'd|I'll|me|my|mine)\b",
        prose,
        flags=re.I,
    ))


def get_prose(text):
    """Strip frontmatter, code fences, inline code, HTML embeds, HTML tags, comments."""
    parts = text.split('---', 2)
    body = parts[2] if len(parts) > 2 else text
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    body = re.sub(r'```.*?```', '', body, flags=re.S)
    body = re.sub(r'`[^`]+`', '', body)
    body = re.sub(r'\]\([^)]*\)', ']', body)
    body = re.sub(r'<div class="visual-wrapper">.*?</div>\s*</div>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', '', body)
    return body


def check_post(path):
    path = pathlib.Path(path)
    text = path.read_text(encoding='utf-8')
    prose = get_prose(text)
    issues = []  # (severity, rule, line_hint, message)

    # ── 1. Paragraph sentence limit ─────────────────────────────────────
    try:
        post = fm_lib.load(path)
        body = post.content
    except Exception:
        body = text
    for line, sentence_count, snippet in paragraph_sentence_violations(body):
        issues.append((
            'error',
            'paragraph-length',
            line,
            f'{sentence_count} sentences in one paragraph (maximum 2): {snippet}'
        ))

    # ── 2. Personal voice ───────────────────────────────────────────────
    personal_signals = first_person_count(body)
    if personal_signals == 0:
        issues.append((
            'info',
            'personal-voice',
            None,
            'No first-person references found. Add one only if a real opinion, decision, '
            'or experience would make the article more useful.'
        ))

    # ── 3. Em dashes ───────────────────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if '—' in line:
            snippet = line.strip()[:90]
            issues.append(('error', 'em-dash', i, f'Em dash: {snippet}'))

    # ── 3. Double dashes in prose ──────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if re.search(r'(?<!\-)\-\-(?!\-)', line):
            issues.append(('warning', 'double-dash', i, f'Double dash: {line.strip()[:90]}'))

    # ── 4. Prose semicolons ────────────────────────────────────────────
    for i, line in enumerate(prose.splitlines(), 1):
        if line.lstrip().startswith(("|", ">")):
            continue
        if re.search(r'\w;', line):
            issues.append(('warning', 'semicolon', i, f'Semicolon in prose: {line.strip()[:90]}'))

    # ── 5. Contrastive parallelism ─────────────────────────────────────
    for pat, label in CONTRASTIVE_PATTERNS:
        for m in re.finditer(pat, prose, re.I):
            start = max(0, m.start() - 20)
            snippet = prose[start:m.start() + 80].replace('\n', ' ').strip()
            issues.append(('error', 'contrastive', None, f'{label}: "...{snippet}..."'))

    # ── 6. Horizontal lines in prose body ─────────────────────────────
    parts = text.split('---', 2)
    if len(parts) > 2:
        body_no_code = re.sub(r'```.*?```', '', parts[2], flags=re.S)
        for i, line in enumerate(body_no_code.splitlines(), 1):
            if re.match(r'^---+\s*$', line):
                issues.append(('error', 'hr', i, f'Horizontal line (---) in prose body'))

    # ── 7. Banned sentence starters ───────────────────────────────────
    for sentence in re.split(r'(?<=[.!?])\s+', prose):
        s = sentence.strip()
        if not s or s[0] in '#-*>|':
            continue
        m = re.match(r'[*_"\']*([A-Za-z]+)', s)
        if m and m.group(1).lower() in BANNED_STARTERS:
            snippet = s[:80]
            issues.append(('warning', 'banned-starter',
                            None, f'Sentence starts with "{m.group(1)}": {snippet}'))

    # ── 8. Forbidden jargon words ──────────────────────────────────────
    for word, suggestion in FORBIDDEN_WORDS.items():
        for m in re.finditer(r'\b' + word + r'\b', prose, re.I):
            start = max(0, m.start() - 20)
            snippet = prose[start:m.start() + 60].replace('\n', ' ').strip()
            issues.append(('error', 'jargon', None,
                            f'Forbidden word "{m.group(0)}" (use: {suggestion}): ...{snippet}...'))

    # ── 9. Rule-of-three language ─────────────────────────────────────
    # A factual count, version, identifier, or explicit factual trio must
    # carry a nearby invisible evidence receipt. Versions such as Python 3.13
    # are excluded because the numeric token is part of the version.
    for m in re.finditer(r'\bthree\b|(?<![\d.])3(?![\d.])', prose, re.I):
        receipt_window = prose[max(0, m.start() - 300):m.start()]
        if '<!-- evidence-three:' in receipt_window:
            continue
        start = max(0, m.start() - 30)
        snippet = prose[start:m.start() + 70].replace('\n', ' ').strip()
        issues.append(('error', 'rule-of-three', None,
                       f'"{m.group(0)}" needs an evidenced count or an explicit factual trio: ...{snippet}...'))

    # ── 10. Frontmatter: missing explicit slug ─────────────────────────
    try:
        post = fm_lib.load(path)
        if not post.get('slug'):
            issues.append(('warning', 'no-slug', None,
                            'No explicit slug in frontmatter — URL will use filename'))
        if not post.get('description'):
            issues.append(('warning', 'no-desc', None, 'No description in frontmatter'))
    except Exception:
        pass

    # ── 11. Missing visual embed ───────────────────────────────────────
    if 'static/visuals' not in text and 'static/images/' not in text:
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
    check_all_statuses = '--all' in args
    args = [a for a in args if a not in ('--summary', '--all')]

    if args:
        paths = [pathlib.Path(a) for a in args]
    else:
        paths = list((ROOT / 'content/posts').glob('*.md'))
        if not check_all_statuses:
            paths = [
                path for path in paths
                if fm_lib.load(path).get('status', 'draft') == 'published'
            ]

    counts, post_counts = check_all(paths, summary_only=summary_only)

    print(f'\n{"─"*60}')
    print(f'TOTAL: {counts["error"]} errors, {counts["warning"]} warnings, {counts["info"]} info')
    if post_counts:
        worst = sorted(post_counts.items(), key=lambda x: -x[1])[:5]
        print(f'Top offenders: {", ".join(n for n,_ in worst)}')
    if counts['error']:
        sys.exit(1)
