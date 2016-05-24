import json
from parsedegrees import *
from units import *
import testutils

class MapLayout:
    def __init__ (self):
        self.paper_width_mm = inch_to_mm (11)
        self.paper_height_mm = inch_to_mm (8.5)

    def parse_json (self, str):
        parsed = json.loads (str)

        if "paper-width" in parsed:
            self.paper_width_mm = parsed["paper-width"]

        if "paper-height" in parsed:
            self.paper_height_mm = parsed["paper-height"]

class TestMapLayout (testutils.TestCaseHelper):
    def test_map_layout_has_us_letter_default_paper_size (self):
        layout = MapLayout ()

        self.assertFloatEquals (layout.paper_width_mm, inch_to_mm (11.0))
        self.assertFloatEquals (layout.paper_height_mm, inch_to_mm (8.5))

    def test_map_layout_parses_numeric_paper_size (self):
        paper_size_numeric = """
{
  "paper-width" : 50.8,
  "paper-height" : 25.4
}
"""

        layout = MapLayout ()
        layout.parse_json (paper_size_numeric)

        self.assertFloatEquals (layout.paper_width_mm, 50.8)
        self.assertFloatEquals (layout.paper_height_mm, 25.4)
