import json
from parsedegrees import *
from units import *
import testutils

class MapLayout:
    def __init__ (self):
        # Sane defaults for if a config file is not specified

        self.paper_width_mm = inch_to_mm (11)
        self.paper_height_mm = inch_to_mm (8.5)
        self.zoom = 15

        self.center_lat      = -96.9040473
        self.center_lon      = 19.4621106
        self.map_scale_denom = 50000

    def parse_json (self, str):
        parsed = json.loads (str)

        if "paper-width" in parsed:
            self.paper_width_mm = parse_units_value (parsed["paper-width"])

        if "paper-height" in parsed:
            self.paper_height_mm = parse_units_value (parsed["paper-height"])

        if "zoom" in parsed:
            self.zoom = parsed["zoom"]

        if "center-lon" in parsed:
            self.center_lon = parse_degrees_value (parsed["center-lon"])

        if "center-lat" in parsed:
            self.center_lat = parse_degrees_value (parsed["center-lat"])

        if "map-scale" in parsed:
            self.map_scale_denom = parsed["map-scale"]

#################### tests ####################

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

    def test_map_layout_parses_inches_paper_size (self):
        paper_size_numeric = """
{
  "paper-width" : "11 in",
  "paper-height" : "8.5 in"
}
"""

        layout = MapLayout ()
        layout.parse_json (paper_size_numeric)

        self.assertFloatEquals (layout.paper_width_mm, inch_to_mm (11))
        self.assertFloatEquals (layout.paper_height_mm, inch_to_mm (8.5))

    def test_map_layout_parses_zoom (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "zoom" : 15 }
        """)

        self.assertEqual (layout.zoom, 15)

    def test_map_layout_parses_center_lon_and_lat (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "center-lat" : "19d27m43s",
            "center-lon" : -96.9040473 }
        """)

        self.assertFloatEquals (layout.center_lat, parse_degrees ("19d27m43s"))
        self.assertFloatEquals (layout.center_lon, -96.9040473)

    def test_map_layout_parses_map_scale (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "map-scale" : 50000 }
        """)

        self.assertFloatEquals (layout.map_scale_denom, 50000)

    def test_map_layout_has_default_center_and_scale (self):
        layout = MapLayout ()
        self.assertFloatEquals (layout.center_lat, -96.9040473)
        self.assertFloatEquals (layout.center_lon, 19.4621106)
        self.assertFloatEquals (layout.map_scale_denom, 50000)
