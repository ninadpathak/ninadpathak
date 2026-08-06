import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "static" / "templates" / "flowchart_generator.py"
SPEC_PATH = ROOT / "static" / "templates" / "documentation-placement-flowchart.json"
CSS_PATH = ROOT / "static" / "css" / "main.css"

spec = importlib.util.spec_from_file_location("flowchart_generator", SCRIPT)
flowchart = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = flowchart
spec.loader.exec_module(flowchart)


class FlowchartGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.chart = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    def test_palette_is_derived_from_the_light_site_tokens(self):
        palette = flowchart.load_site_palette(CSS_PATH)
        self.assertEqual(
            palette,
            {
                "background": "#f8f8f6",
                "surface": "#ffffff",
                "surface_muted": "#efefed",
                "border": "#e0e0dc",
                "border_strong": "#c8c8c4",
                "ink": "#0e0e0e",
                "text": "#3a3a3a",
                "accent": "#d44000",
            },
        )

    def test_layout_fits_the_real_prose_slot_at_desktop_and_mobile(self):
        layout = flowchart.build_layout(self.chart)
        self.assertEqual(layout.canvas_width, 672)
        self.assertEqual(layout.desktop_render_width, 672)
        self.assertEqual(layout.mobile_render_width, 342)
        self.assertGreaterEqual(layout.minimum_rendered_font_size(), 13)
        self.assertGreater(layout.canvas_height, 0)
        self.assertLessEqual(layout.canvas_height, 1200)
        flowchart.validate_layout(layout)

    def test_layout_has_no_box_overlap_or_clipping(self):
        layout = flowchart.build_layout(self.chart)
        for box in layout.boxes.values():
            self.assertGreaterEqual(box.x, 0)
            self.assertGreaterEqual(box.y, 0)
            self.assertLessEqual(box.right, layout.canvas_width)
            self.assertLessEqual(box.bottom, layout.canvas_height)
        for left, right in flowchart.pairs(layout.boxes.values()):
            self.assertFalse(flowchart.intersects(left, right), f"{left.node_id} overlaps {right.node_id}")

    def test_each_connector_starts_and_ends_on_the_expected_box_boundary(self):
        layout = flowchart.build_layout(self.chart)
        for connector in layout.connectors:
            source = layout.boxes[connector.source]
            target = layout.boxes[connector.target]
            self.assertEqual(connector.points[0], (source.center_x, source.bottom))
            self.assertEqual(connector.points[-1], (target.center_x, target.y))

    def test_connectors_route_around_unrelated_nodes(self):
        layout = flowchart.build_layout(self.chart)
        for connector in layout.connectors:
            for box in layout.boxes.values():
                if box.node_id not in {connector.source, connector.target}:
                    self.assertFalse(
                        flowchart.connector_intersects_box(connector, box),
                        f"{connector.source}->{connector.target} crosses {box.node_id}",
                    )

    def test_skipped_layer_is_rejected_before_it_can_create_an_ambiguous_route(self):
        invalid = json.loads(json.dumps(self.chart))
        invalid["edges"].append({"from": "reader-task", "to": "internal"})
        with self.assertRaisesRegex(ValueError, "immediately next layer"):
            flowchart.build_layout(invalid)

    def test_svg_uses_only_the_derived_site_palette_and_is_deterministic(self):
        first = flowchart.render_svg(self.chart, CSS_PATH)
        second = flowchart.render_svg(self.chart, CSS_PATH)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith('<svg'))
        self.assertTrue(flowchart.svg_uses_only_allowed_colours(first, flowchart.load_site_palette(CSS_PATH)))

    def test_cli_writes_svg_png_and_geometry_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg_path = root / "chart.svg"
            png_path = root / "chart.png"
            receipt_path = root / "chart-layout.json"
            exit_code = flowchart.main([
                "--input", str(SPEC_PATH),
                "--css", str(CSS_PATH),
                "--svg", str(svg_path),
                "--png", str(png_path),
                "--receipt", str(receipt_path),
            ])
            self.assertEqual(exit_code, 0)
            self.assertTrue(svg_path.exists())
            self.assertTrue(png_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["canvas"]["width"], 672)
            self.assertEqual(receipt["render_targets"]["mobile_width"], 342)
            self.assertEqual(len(receipt["boxes"]), 5)
            self.assertEqual(len(receipt["connectors"]), 4)


if __name__ == "__main__":
    unittest.main()
