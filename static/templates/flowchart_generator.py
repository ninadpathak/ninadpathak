#!/usr/bin/env python3
"""Render validated, site-token flow charts from structured JSON input.

The layout is derived from the site's prose slot, not an arbitrary image ratio.
Each node is measured from wrapped text, laid out on a two-column grid, and
validated before SVG or PNG output is written.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

CSS_TOKEN_MAP = {
    "background": "--bg",
    "surface": "--bg-1",
    "surface_muted": "--bg-2",
    "border": "--border",
    "border_strong": "--border-2",
    "ink": "--text-1",
    "text": "--text-2",
    "accent": "--accent",
}

DEFAULTS = {
    "mobile_viewport": 390,
    "minimum_mobile_font_size": 13,
    "columns": 2,
    "outer_padding": 24,
    "column_gap": 24,
    "row_gap": 52,
    "node_padding_x": 20,
    "node_padding_y": 20,
    "title_line_height": 1.24,
    "body_line_height": 1.42,
    "title_to_body_gap": 10,
    "max_canvas_height": 1200,
}


@dataclass(frozen=True)
class Box:
    node_id: str
    x: int
    y: int
    width: int
    height: int
    title_lines: tuple[str, ...]
    body_lines: tuple[str, ...]
    kind: str

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2


@dataclass(frozen=True)
class Connector:
    source: str
    target: str
    label: str
    points: tuple[tuple[int, int], ...]
    label_x: int
    label_y: int


@dataclass(frozen=True)
class Layout:
    canvas_width: int
    canvas_height: int
    desktop_render_width: int
    mobile_render_width: int
    scale_at_mobile: float
    title_font_size: int
    body_font_size: int
    label_font_size: int
    title_line_height: int
    body_line_height: int
    boxes: dict[str, Box]
    connectors: tuple[Connector, ...]
    palette: dict[str, str]

    def minimum_rendered_font_size(self) -> float:
        return min(self.title_font_size, self.body_font_size, self.label_font_size) / self.scale_at_mobile


def pairs(values: Iterable[Box]):
    return combinations(values, 2)


def intersects(left: Box, right: Box) -> bool:
    return left.x < right.right and right.x < left.right and left.y < right.bottom and right.y < left.bottom


def _root_block(css: str) -> str:
    match = re.search(r":root\s*\{(?P<body>.*?)\}", css, re.S)
    if not match:
        raise ValueError("CSS has no :root token block")
    return match.group("body")


def _css_value(source: str, name: str) -> str:
    match = re.search(rf"{re.escape(name)}\s*:\s*([^;]+);", source)
    if not match:
        raise ValueError(f"CSS token missing: {name}")
    return match.group(1).strip()


def load_site_palette(css_path: Path) -> dict[str, str]:
    root = _root_block(css_path.read_text(encoding="utf-8"))
    palette = {name: _css_value(root, token).lower() for name, token in CSS_TOKEN_MAP.items()}
    invalid = {name: value for name, value in palette.items() if not re.fullmatch(r"#[0-9a-f]{6}", value)}
    if invalid:
        raise ValueError(f"site palette requires six-digit hex tokens: {invalid}")
    return palette


def load_site_geometry(css_path: Path, mobile_viewport: int) -> tuple[int, int]:
    css = css_path.read_text(encoding="utf-8")
    root = _root_block(css)
    prose_width = _css_value(root, "--prose-w")
    if not prose_width.endswith("px"):
        raise ValueError("--prose-w must use px")
    container = re.search(r"\.prose-container\s*\{(?P<body>.*?)\}", css, re.S)
    if not container:
        raise ValueError("CSS has no .prose-container rule")
    padding = re.search(r"padding\s*:\s*0\s+([0-9.]+)rem", container.group("body"))
    if not padding:
        raise ValueError(".prose-container must have symmetric rem padding")
    horizontal_padding = round(float(padding.group(1)) * 16)
    desktop_width = int(prose_width[:-2]) - 2 * horizontal_padding
    mobile_width = mobile_viewport - 2 * horizontal_padding
    if desktop_width <= 0 or mobile_width <= 0:
        raise ValueError("prose geometry produces a non-positive render width")
    return desktop_width, min(desktop_width, mobile_width)


def wrap_text(text: str, width: int, font_size: int, weight: str) -> tuple[str, ...]:
    if not text.strip():
        return ()
    # Inter's average glyph width is conservatively approximated so line breaks
    # happen before text can touch node padding. Wide glyphs get extra margin.
    glyph_factor = 0.56 if weight == "title" else 0.52
    capacity = max(8, int(width / (font_size * glyph_factor)))
    words = text.split()
    lines: list[str] = []
    line: list[str] = []
    for word in words:
        candidate = " ".join([*line, word])
        if line and len(candidate) > capacity:
            lines.append(" ".join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(" ".join(line))
    return tuple(lines)


def _validate_spec(chart: dict) -> None:
    nodes = chart.get("nodes")
    edges = chart.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("chart requires a non-empty nodes list")
    if not isinstance(edges, list):
        raise ValueError("chart requires an edges list")
    ids = [node.get("id") for node in nodes]
    if any(not isinstance(node_id, str) or not node_id for node_id in ids) or len(set(ids)) != len(ids):
        raise ValueError("node ids must be unique non-empty strings")
    for node in nodes:
        if not isinstance(node.get("layer"), int) or node["layer"] < 0:
            raise ValueError(f"node {node['id']} needs a non-negative integer layer")
        if not str(node.get("title", "")).strip():
            raise ValueError(f"node {node['id']} needs a title")
        if node.get("kind", "decision") not in {"decision", "outcome"}:
            raise ValueError(f"node {node['id']} has an unsupported kind")
    by_id = {node["id"]: node for node in nodes}
    for edge in edges:
        if edge.get("from") not in by_id or edge.get("to") not in by_id:
            raise ValueError("edges must reference known nodes")
        if by_id[edge["to"]]["layer"] != by_id[edge["from"]]["layer"] + 1:
            raise ValueError("edges must point to the immediately next layer")


def build_layout(chart: dict, css_path: Path | None = None) -> Layout:
    _validate_spec(chart)
    config = {**DEFAULTS, **chart.get("layout", {})}
    if css_path is None:
        css_path = Path(__file__).resolve().parents[1] / "css" / "main.css"
    desktop_width, mobile_width = load_site_geometry(css_path, int(chart.get("mobile_viewport", config["mobile_viewport"])))
    palette = load_site_palette(css_path)
    scale_at_mobile = desktop_width / mobile_width
    title_font = math.ceil(int(config["minimum_mobile_font_size"]) * scale_at_mobile)
    body_font = title_font
    label_font = title_font
    title_line_height = math.ceil(title_font * float(config["title_line_height"]))
    body_line_height = math.ceil(body_font * float(config["body_line_height"]))
    columns = int(config["columns"])
    if columns < 1:
        raise ValueError("columns must be at least one")

    nodes_by_layer: dict[int, list[dict]] = {}
    for node in chart["nodes"]:
        nodes_by_layer.setdefault(node["layer"], []).append(node)
    if any(len(nodes) > columns for nodes in nodes_by_layer.values()):
        raise ValueError("a layer contains more nodes than the configured columns")
    if sorted(nodes_by_layer) != list(range(max(nodes_by_layer) + 1)):
        raise ValueError("layers must be contiguous from zero")

    outer = int(config["outer_padding"])
    gap = int(config["column_gap"])
    node_padding_x = int(config["node_padding_x"])
    node_padding_y = int(config["node_padding_y"])
    grid_width = desktop_width - 2 * outer
    column_width = (grid_width - (columns - 1) * gap) // columns
    if column_width <= 2 * node_padding_x:
        raise ValueError("node grid leaves no text width")

    prepared: dict[str, tuple[dict, int, tuple[str, ...], tuple[str, ...], int]] = {}
    row_heights: dict[int, int] = {}
    for layer, nodes in nodes_by_layer.items():
        for node in nodes:
            width = grid_width if len(nodes) == 1 else column_width
            inner_width = width - 2 * node_padding_x
            title_lines = wrap_text(str(node["title"]), inner_width, title_font, "title")
            body_lines = wrap_text(str(node.get("body", "")), inner_width, body_font, "body")
            height = node_padding_y * 2 + len(title_lines) * title_line_height
            if body_lines:
                height += int(config["title_to_body_gap"]) + len(body_lines) * body_line_height
            prepared[node["id"]] = (node, width, title_lines, body_lines, height)
            row_heights[layer] = max(row_heights.get(layer, 0), height)

    boxes: dict[str, Box] = {}
    y = outer
    for layer in sorted(nodes_by_layer):
        nodes = nodes_by_layer[layer]
        row_width = grid_width if len(nodes) == 1 else len(nodes) * column_width + (len(nodes) - 1) * gap
        x = outer + (grid_width - row_width) // 2
        for node in nodes:
            _, width, title_lines, body_lines, _ = prepared[node["id"]]
            boxes[node["id"]] = Box(node["id"], x, y, width, row_heights[layer], title_lines, body_lines, node.get("kind", "decision"))
            x += width + gap
        y += row_heights[layer] + int(config["row_gap"])
    canvas_height = y - int(config["row_gap"]) + outer
    if canvas_height > int(config["max_canvas_height"]):
        raise ValueError(f"canvas height {canvas_height} exceeds max_canvas_height")

    connectors: list[Connector] = []
    for edge in chart["edges"]:
        source, target = boxes[edge["from"]], boxes[edge["to"]]
        mid_y = (source.bottom + target.y) // 2
        direct = ((source.center_x, source.bottom), (source.center_x, mid_y), (target.center_x, mid_y), (target.center_x, target.y))
        unrelated = [box for node_id, box in boxes.items() if node_id not in {source.node_id, target.node_id}]
        if any(polyline_intersects_box(direct, box) for box in unrelated):
            lane_x = outer // 2 if source.center_x <= desktop_width // 2 else desktop_width - outer // 2
            points = ((source.center_x, source.bottom), (lane_x, source.bottom), (lane_x, target.y), (target.center_x, target.y))
            if any(polyline_intersects_box(points, box) for box in unrelated):
                raise ValueError(f"no clear connector route for {source.node_id}->{target.node_id}")
            label_x = (source.center_x + lane_x) // 2
            label_y = source.bottom + label_font
        else:
            points = direct
            label_x = (source.center_x + target.center_x) // 2
            label_y = mid_y - 8
        connectors.append(Connector(edge["from"], edge["to"], str(edge.get("label", "")), points, label_x, label_y))

    layout = Layout(desktop_width, canvas_height, desktop_width, mobile_width, scale_at_mobile, title_font, body_font, label_font, title_line_height, body_line_height, boxes, tuple(connectors), palette)
    validate_layout(layout)
    return layout


def segment_intersects_box(start: tuple[int, int], end: tuple[int, int], box: Box) -> bool:
    """Return true when an orthogonal segment crosses a box interior."""
    x1, y1 = start
    x2, y2 = end
    if y1 == y2:
        return box.y < y1 < box.bottom and min(x1, x2) < box.right and max(x1, x2) > box.x
    if x1 == x2:
        return box.x < x1 < box.right and min(y1, y2) < box.bottom and max(y1, y2) > box.y
    raise ValueError("connector segments must be orthogonal")


def polyline_intersects_box(points: tuple[tuple[int, int], ...], box: Box) -> bool:
    return any(segment_intersects_box(start, end, box) for start, end in zip(points, points[1:]))


def connector_intersects_box(connector: Connector, box: Box) -> bool:
    return polyline_intersects_box(connector.points, box)


def validate_layout(layout: Layout) -> None:
    if layout.minimum_rendered_font_size() < 13:
        raise ValueError("smallest rendered font is below 13px at the mobile target")
    for box in layout.boxes.values():
        if box.x < 0 or box.y < 0 or box.right > layout.canvas_width or box.bottom > layout.canvas_height:
            raise ValueError(f"node {box.node_id} is outside the canvas")
    for left, right in pairs(layout.boxes.values()):
        if intersects(left, right):
            raise ValueError(f"nodes overlap: {left.node_id}, {right.node_id}")
    for connector in layout.connectors:
        source, target = layout.boxes[connector.source], layout.boxes[connector.target]
        if connector.points[0] != (source.center_x, source.bottom) or connector.points[-1] != (target.center_x, target.y):
            raise ValueError(f"connector {connector.source}->{connector.target} misses a box boundary")
        for node_id, box in layout.boxes.items():
            if node_id not in {connector.source, connector.target} and connector_intersects_box(connector, box):
                raise ValueError(f"connector {connector.source}->{connector.target} crosses {node_id}")
        if not 0 <= connector.label_x <= layout.canvas_width or not 0 <= connector.label_y <= layout.canvas_height:
            raise ValueError(f"connector label {connector.source}->{connector.target} is outside the canvas")


def _text_lines(lines: tuple[str, ...], x: int, y: int, line_height: int, class_name: str) -> str:
    return "".join(f'<text class="{class_name}" x="{x}" y="{y + index * line_height}">{html.escape(line)}</text>' for index, line in enumerate(lines))


def render_svg(chart: dict, css_path: Path | None = None) -> str:
    layout = build_layout(chart, css_path)
    p = layout.palette
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{layout.canvas_width}" height="{layout.canvas_height}" viewBox="0 0 {layout.canvas_width} {layout.canvas_height}" preserveAspectRatio="xMidYMin meet" role="img" aria-label="{html.escape(str(chart.get("title", "Flow chart")))}">',
        "<style>",
        f".node{{fill:{p['surface']};stroke:{p['border_strong']};stroke-width:1.5}}",
        f".outcome{{stroke:{p['border']}}}",
        f".edge{{fill:none;stroke:{p['border_strong']};stroke-width:1.5;stroke-linecap:square;stroke-linejoin:miter}}",
        f".accent{{fill:{p['accent']}}}",
        f".title{{fill:{p['ink']};font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:{layout.title_font_size}px;font-weight:600;letter-spacing:-0.02em}}",
        f".body{{fill:{p['text']};font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:{layout.body_font_size}px;font-weight:400}}",
        f".edge-label{{fill:{p['accent']};font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:{layout.label_font_size}px;font-weight:600;text-transform:uppercase}}",
        "</style>",
        f'<rect width="100%" height="100%" fill="{p["background"]}"/>',
    ]
    for connector in layout.connectors:
        path = " ".join(("M" if index == 0 else "L") + f"{x} {y}" for index, (x, y) in enumerate(connector.points))
        parts.append(f'<path class="edge" d="{path}"/>')
        if connector.label:
            parts.append(f'<text class="edge-label" text-anchor="middle" x="{connector.label_x}" y="{connector.label_y}">{html.escape(connector.label.upper())}</text>')
    for box in layout.boxes.values():
        parts.append(f'<rect class="node {"outcome" if box.kind == "outcome" else ""}" x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" rx="2"/>')
        if box.kind == "outcome":
            parts.append(f'<rect class="accent" x="{box.x}" y="{box.y}" width="{box.width}" height="6"/>')
        text_y = box.y + int(DEFAULTS["node_padding_y"]) + layout.title_font_size
        parts.append(_text_lines(box.title_lines, box.x + int(DEFAULTS["node_padding_x"]), text_y, layout.title_line_height, "title"))
        if box.body_lines:
            body_y = text_y + len(box.title_lines) * layout.title_line_height + int(DEFAULTS["title_to_body_gap"])
            parts.append(_text_lines(box.body_lines, box.x + int(DEFAULTS["node_padding_x"]), body_y, layout.body_line_height, "body"))
    parts.append("</svg>")
    svg = "".join(parts)
    if not svg_uses_only_allowed_colours(svg, p):
        raise ValueError("rendered SVG contains a colour outside the site palette")
    return svg


def svg_uses_only_allowed_colours(svg: str, palette: dict[str, str]) -> bool:
    colours = {match.lower() for match in re.findall(r"#[0-9A-Fa-f]{3,6}\b", svg)}
    return colours <= set(palette.values())


def receipt(layout: Layout) -> dict:
    return {
        "canvas": {"width": layout.canvas_width, "height": layout.canvas_height},
        "render_targets": {"desktop_width": layout.desktop_render_width, "mobile_width": layout.mobile_render_width, "mobile_scale": layout.scale_at_mobile},
        "typography": {"title_source_px": layout.title_font_size, "body_source_px": layout.body_font_size, "label_source_px": layout.label_font_size, "minimum_mobile_px": round(layout.minimum_rendered_font_size(), 2)},
        "palette": layout.palette,
        "boxes": {node_id: asdict(box) for node_id, box in layout.boxes.items()},
        "connectors": [asdict(connector) for connector in layout.connectors],
    }


def render_png(svg_path: Path, png_path: Path, source_width: int) -> None:
    renderer = shutil.which("rsvg-convert")
    if not renderer:
        raise RuntimeError("rsvg-convert is required for deterministic PNG rendering")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([renderer, "--format=png", "--width", str(source_width * 2), "--output", str(png_path), str(svg_path)], check=True)


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--css", type=Path, default=here.parent / "css" / "main.css")
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        chart = json.loads(args.input.read_text(encoding="utf-8"))
        layout = build_layout(chart, args.css)
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(render_svg(chart, args.css), encoding="utf-8")
        render_png(args.svg, args.png, layout.canvas_width)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt(layout), indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"FLOWCHART FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"FLOWCHART PASSED: {len(layout.boxes)} nodes, {len(layout.connectors)} connectors")
    print(f"Canvas: {layout.canvas_width}×{layout.canvas_height}; mobile font floor: {layout.minimum_rendered_font_size():.2f}px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
