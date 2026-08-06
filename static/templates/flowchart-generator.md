# Flow-chart generator

`flowchart_generator.py` turns a structured JSON chart into deterministic SVG, 2× PNG, and a geometry receipt.

## Design contract

The generator reads the light-theme token values and prose geometry from `static/css/main.css`.

- **Desktop canvas:** the actual prose-content slot, currently 672px wide from `--prose-w` minus container padding.
- **Mobile target:** the actual 390px viewport content slot, currently 342px wide.
- **Typography floor:** every rendered chart font must remain at least 13px at the mobile target.
- **Grid:** two columns, 24px outer padding and gap, 52px row gap. Node height is calculated from wrapped title/body lines plus padding.
- **Routing:** edges must connect only adjacent layers. This prevents a connector from passing through a node and forces an ambiguous decision tree to be redesigned or split before rendering.
- **Validation:** the tool rejects unknown nodes, non-contiguous layers, boxes outside canvas, overlapping boxes, obstructed connectors, labels outside canvas, unsupported colors, or a chart taller than 1200px.
- **Palette:** background, surfaces, borders, ink, text, and accent are read from current CSS tokens. The SVG is rejected if it emits any other hex color.

Use the supplied JSON fixture as a starting point. Each node needs `id`, `layer`, `title`, and `kind`. `body` is optional. Edges use `from`, `to`, and optional `label`.

## Run

```bash
.venv/bin/python static/templates/flowchart_generator.py \
  --input static/templates/documentation-placement-flowchart.json \
  --css static/css/main.css \
  --svg /tmp/flowchart.svg \
  --png /tmp/flowchart@2x.png \
  --receipt /tmp/flowchart-layout.json
```

The JSON receipt records canvas dimensions, desktop/mobile render targets, source font sizes, mobile font floor, palette, node bounds, and connector points. Preserve it with any published diagram package.
