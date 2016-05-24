import json
from parsedegrees import *
from units import *
import testutils

letter_paper_size_numeric = """
{
  "paper-width" : 279.4,
  "paper-height" : 215.9
}
"""

class MapLayout:
    def __init__ (self):
        self.paper_width_mm = inch_to_mm (11)
        self.paper_height_mm = inch_to_mm (8.5)

class TestMapLayout (testutils.TestCaseHelper):
    def test_map_layout_has_us_letter_default_paper_size (self):
        layout = MapLayout ()

        self.assertFloatEquals (layout.paper_width_mm, inch_to_mm (11.0))
        self.assertFloatEquals (layout.paper_height_mm, inch_to_mm (8.5))
