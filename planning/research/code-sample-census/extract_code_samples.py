#!/usr/bin/env python3
"""Generator-aware tier-1 extractor for the code-sample census pilot."""

from __future__ import annotations

import argparse
import ast
import doctest
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, Tag

PYTHON_CLASSES = {
    "highlight-python": "python",
    "language-python": "python",
    "language-py": "python",
    "highlight-pycon": "pycon",
    "language-pycon": "pycon",
    "language-python-console": "pycon",
}
PYTHON_ATTRS = {"python": "python", "py": "python", "pycon": "pycon", "python-console": "pycon"}
PROMPT = re.compile(r"(?m)^\s*>>>")


@dataclass(frozen=True)
class Sample:
    block_id: str
    url: str
    ordinal: int
    generator: str
    kind: str
    evidence: str
    source: str
    source_sha256: str
    parses: bool
    parse_error: str | None
    audit_classification: None = None


def meta_generators(soup: BeautifulSoup) -> list[str]:
    return [
        str(meta.get("content", "")).strip()
        for meta in soup.find_all("meta")
        if str(meta.get("name", "")).lower() == "generator" and meta.get("content")
    ]


def detect_generator(soup: BeautifulSoup) -> str:
    declared = " ".join(meta_generators(soup)).lower()
    if "sphinx" in declared:
        return "sphinx"
    if "mkdocs" in declared:
        return "mkdocs"
    if "docusaurus" in declared:
        return "docusaurus"
    if "mintlify" in declared:
        return "mintlify"
    if "starlight" in declared or "astro" in declared:
        return "starlight"

    if soup.find(id="__docusaurus"):
        return "docusaurus"
    if soup.select_one(".md-content") and soup.select_one("[data-md-component]"):
        return "mkdocs"
    if soup.find("script", src=re.compile(r"(?:^|/)_static/documentation_options\.js")):
        return "sphinx"
    if soup.select_one(".sphinxsidebar, .sphinxsidebarwrapper"):
        return "sphinx"
    return "unknown"


def node_classes(node: Tag) -> set[str]:
    classes: set[str] = set()
    current: Tag | None = node
    for _ in range(5):
        if current is None:
            break
        classes.update(str(item).lower() for item in current.get("class", []))
        current = current.parent if isinstance(current.parent, Tag) else None
    return classes


def language_evidence(pre: Tag, generator: str) -> tuple[str, str] | None:
    code = pre.find("code")
    nodes = [pre] + ([code] if isinstance(code, Tag) else [])
    for node in nodes:
        classes = node_classes(node)
        for class_name, kind in PYTHON_CLASSES.items():
            if class_name in classes:
                return kind, f"class:{class_name}"
        current: Tag | None = node
        for _ in range(5):
            if current is None:
                break
            for attr in ("data-language", "data-lang"):
                value = str(current.get(attr, "")).strip().lower()
                if value in PYTHON_ATTRS:
                    return PYTHON_ATTRS[value], f"{attr}:{value}"
            current = current.parent if isinstance(current.parent, Tag) else None

    source = extract_text(pre)
    if generator in {"sphinx", "mkdocs"} and PROMPT.search(source):
        return "pycon", "prompt:>>>"
    return None


def extract_text(pre: Tag) -> str:
    """Preserve source whitespace where HTML text nodes contain it.

    Custom renderers that split every token into layout spans without source
    whitespace remain unsupported rather than being reconstructed by guesswork.
    """
    code = pre.find("code")
    node = code if isinstance(code, Tag) else pre
    text = node.get_text(separator="", strip=False).replace("\u00a0", " ")
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def parse_python(source: str) -> tuple[bool, str | None]:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        return False, f"{exc.__class__.__name__}: line {exc.lineno}: {exc.msg}"
    return True, None


def parse_pycon(source: str) -> tuple[bool, str | None]:
    examples = doctest.DocTestParser().get_examples(source)
    if not examples:
        return False, "ExtractionError: no doctest inputs found"
    for index, example in enumerate(examples, start=1):
        ok, error = parse_python(example.source)
        if not ok:
            return False, f"example {index}: {error}"
    return True, None


def iter_samples(html: str | bytes, url: str) -> tuple[str, list[Sample], dict[str, int]]:
    soup = BeautifulSoup(html, "html.parser")
    generator = detect_generator(soup)
    pres = soup.find_all("pre")
    if generator == "unknown":
        return generator, [], {"pre_blocks": len(pres), "included": 0, "excluded": len(pres)}

    samples: list[Sample] = []
    for ordinal, pre in enumerate(pres, start=1):
        evidence = language_evidence(pre, generator)
        if evidence is None:
            continue
        kind, reason = evidence
        source = extract_text(pre)
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        identity = f"{url}\0{ordinal}\0{source_hash}".encode("utf-8")
        block_id = hashlib.sha256(identity).hexdigest()[:20]
        parses, error = parse_pycon(source) if kind == "pycon" else parse_python(source)
        samples.append(
            Sample(
                block_id=block_id,
                url=url,
                ordinal=ordinal,
                generator=generator,
                kind=kind,
                evidence=reason,
                source=source,
                source_sha256=source_hash,
                parses=parses,
                parse_error=error,
            )
        )
    return generator, samples, {
        "pre_blocks": len(pres),
        "included": len(samples),
        "excluded": len(pres) - len(samples),
    }


def serialize(samples: Iterable[Sample]) -> list[dict[str, object]]:
    return [asdict(sample) for sample in samples]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    raw = args.html.read_bytes()
    generator, samples, counts = iter_samples(raw, args.url)
    result = {"url": args.url, "generator": generator, "counts": counts, "samples": serialize(samples)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
