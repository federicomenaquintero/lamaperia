from parsedegrees import *
from units import *
import testutils

# The following values are declared here instead of
# MapLayout.__init__() so that we can use the same values in the unit
# tests.
#
# You can also change these values if you want different defaults
# when not using a configuration file.  May I suggest that you
# make a known-good configuration file instead and base the
# rest of your work on that.
#

default_draw_map_frame = True
default_draw_ticks     = True
default_draw_map       = True
default_draw_scale     = True

default_paper_width_mm  = inch_to_mm (11)
default_paper_height_mm = inch_to_mm (8.5)
default_zoom            = 15

default_center_lat      = 19.4621106
default_center_lon      = -96.9040473
default_map_scale_denom = 50000

default_map_width_mm    = inch_to_mm (10)
default_map_height_mm   = inch_to_mm (7.375)

default_map_to_left_margin_mm = inch_to_mm (0.5)
default_map_to_top_margin_mm  = inch_to_mm (0.375)

default_scale_xpos_mm = inch_to_mm (5.5)
default_scale_ypos_mm = inch_to_mm (8.125)

class MapLayout:
    def __init__ (self):
        # Sane defaults for if a config file is not specified

        self.draw_map_frame = default_draw_map_frame
        self.draw_ticks     = default_draw_ticks
        self.draw_map       = default_draw_map
        self.draw_scale     = default_draw_scale

        self.paper_width_mm  = default_paper_width_mm
        self.paper_height_mm = default_paper_height_mm
        self.zoom            = default_zoom

        self.center_lat      = default_center_lat
        self.center_lon      = default_center_lon
        self.map_scale_denom = default_map_scale_denom

        self.map_width_mm    = default_map_width_mm
        self.map_height_mm   = default_map_height_mm

        self.map_to_left_margin_mm = default_map_to_left_margin_mm
        self.map_to_top_margin_mm  = default_map_to_top_margin_mm

        self.scale_xpos_mm = default_scale_xpos_mm
        self.scale_ypos_mm = default_scale_ypos_mm

        self.scale_large_divisions_interval_m = 1000
        self.scale_num_large_divisions = 4

        self.scale_small_divisions_interval_m = 100
        self.scale_num_small_divisions = 10

        self.scale_large_ticks_m = [ 0, "0",
                                     1000, "1",
                                     2000, "2",
                                     3000, "3",
                                     4000, "4 Km" ]

        self.scale_small_ticks_m = [ 0, "0 m",
                                     500, "500",
                                     1000, "1000" ]

    def validate (self):
        if not (type (self.zoom) == int and self.zoom >= 0 and self.zoom <= 19):
            raise ValueError ("Zoom must be an integer in the range [0, 19]")

    def parse_json (self, parsed):
        if "draw-map-frame" in parsed:
            self.draw_map_frame = parsed["draw-map-frame"]

        if "draw-ticks" in parsed:
            self.draw_ticks = parsed["draw-ticks"]

        if "draw-map" in parsed:
            self.draw_map = parsed["draw-map"]

        if "draw-scale" in parsed:
            self.draw_scale = parsed["draw-scale"]

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

        if "map-width" in parsed:
            self.map_width_mm = parse_units_value (parsed["map-width"])

        if "map-height" in parsed:
            self.map_height_mm = parse_units_value (parsed["map-height"])

        if "map-to-left-margin" in parsed:
            self.map_to_left_margin_mm = parse_units_value (parsed["map-to-left-margin"])

        if "map-to-top-margin" in parsed:
            self.map_to_top_margin_mm = parse_units_value (parsed["map-to-top-margin"])

        if "scale-xpos" in parsed:
            self.scale_xpos_mm = parse_units_value (parsed["scale-xpos"])

        if "scale-ypos" in parsed:
            self.scale_ypos_mm = parse_units_value (parsed["scale-ypos"])

        if "scale-large-divisions-interval-m" in parsed:
            self.scale_large_divisions_interval_m = parsed["scale-large-divisions-interval-m"]

        if "scale-num-large-divisions" in parsed:
            self.scale_num_large_divisions = parsed["scale-num-large-divisions"]

        if "scale-small-divisions-interval-m" in parsed:
            self.scale_small_divisions_interval_m = parsed["scale-small-divisions-interval-m"]

        if "scale-num-small-divisions" in parsed:
            self.scale_num_small_divisions = parsed["scale-num-small-divisions"]

        if "scale-large-ticks-m" in parsed:
            self.scale_large_ticks_m = parsed["scale-large-ticks-m"]

        if "scale-small-ticks-m" in parsed:
            self.scale_small_ticks_m = parsed["scale-small-ticks-m"]

#################### tests ####################

class TestMapLayout (testutils.TestCaseHelper):
    def test_map_layout_has_defaults_for_what_to_render (self):
        layout = MapLayout ()

        self.assertEqual (layout.draw_map_frame, default_draw_map_frame)
        self.assertEqual (layout.draw_ticks, default_draw_ticks)
        self.assertEqual (layout.draw_map, default_draw_map)
        self.assertEqual (layout.draw_scale, default_draw_scale)

    def test_map_layout_parses_what_to_render (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "draw-map-frame" : false,
            "draw-ticks"     : false,
            "draw-map"       : false,
            "draw-scale"     : false }
        """)

        self.assertEqual (layout.draw_map_frame, False)
        self.assertEqual (layout.draw_ticks, False)
        self.assertEqual (layout.draw_map, False)
        self.assertEqual (layout.draw_scale, False)

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

    def test_map_layout_has_default_paper_size (self):
        layout = MapLayout ()
        self.assertFloatEquals (layout.paper_width_mm, default_paper_width_mm)
        self.assertFloatEquals (layout.paper_height_mm, default_paper_height_mm)

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
        self.assertFloatEquals (layout.center_lat, default_center_lat)
        self.assertFloatEquals (layout.center_lon, default_center_lon)
        self.assertFloatEquals (layout.map_scale_denom, 50000)

    def test_map_layout_has_default_map_size (self):
        layout = MapLayout ()
        self.assertFloatEquals (layout.map_width_mm, default_map_width_mm)
        self.assertFloatEquals (layout.map_height_mm, default_map_height_mm)

    def test_map_layout_parses_map_width_and_height (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "map-width" : "100 mm",
            "map-height" : "200 mm" }
        """)

        self.assertFloatEquals (layout.map_width_mm, 100)
        self.assertFloatEquals (layout.map_height_mm, 200)

    def test_map_layout_has_default_map_to_top_left_margin (self):
        layout = MapLayout ()
        self.assertFloatEquals (layout.map_to_left_margin_mm, default_map_to_left_margin_mm)
        self.assertFloatEquals (layout.map_to_top_margin_mm, default_map_to_top_margin_mm)

    def test_map_layout_parses_map_to_top_left_margin (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "map-to-left-margin" : "100 mm",
            "map-to-top-margin" : "200 mm" }
        """)

        self.assertFloatEquals (layout.map_to_left_margin_mm, 100)
        self.assertFloatEquals (layout.map_to_top_margin_mm, 200)

    def test_map_layout_has_default_scale_position (self):
        layout = MapLayout ()
        self.assertFloatEquals (layout.scale_xpos_mm, default_scale_xpos_mm)
        self.assertFloatEquals (layout.scale_ypos_mm, default_scale_ypos_mm)

    def test_map_layout_parses_scale_position (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "scale-xpos" : "100 mm",
            "scale-ypos" : "200 mm" }
        """)

        self.assertFloatEquals (layout.scale_xpos_mm, 100)
        self.assertFloatEquals (layout.scale_ypos_mm, 200)

    def test_map_layout_has_defaults_for_scale_parameters (self):
        layout = MapLayout ()

        self.assertEqual (layout.scale_large_divisions_interval_m, 1000)
        self.assertEqual (layout.scale_num_large_divisions, 4)

        self.assertEqual (layout.scale_small_divisions_interval_m, 100)
        self.assertEqual (layout.scale_num_small_divisions, 10)

        self.assertEqual (layout.scale_large_ticks_m, [ 0, "0",
                                                        1000, "1",
                                                        2000, "2",
                                                        3000, "3",
                                                        4000, "4 Km" ])
        self.assertEqual (layout.scale_small_ticks_m, [ 0, "0 m",
                                                        500, "500",
                                                        1000, "1000" ])


    def test_map_layout_parses_scale_parameters (self):
        layout = MapLayout ()
        layout.parse_json ("""
          { "scale-large-divisions-interval-m" : 1000,
            "scale-num-large-divisions" : 4,

            "scale-small-divisions-interval-m" : 100,
            "scale-num-small-divisions" : 10,

            "scale-large-ticks-m" : [ 0, 0,
                                      1000, 1,
                                      2000, 2,
                                      3000, 3,
                                      4000, 4 ],
            "scale-small-ticks-m" : [ 0, 0,
                                      500, 500,
                                      1000, 1000 ]
          }
        """)

        self.assertEqual (layout.scale_large_divisions_interval_m, 1000)
        self.assertEqual (layout.scale_num_large_divisions, 4)

        self.assertEqual (layout.scale_small_divisions_interval_m, 100)
        self.assertEqual (layout.scale_num_small_divisions, 10)

        self.assertEqual (layout.scale_large_ticks_m, [ 0, 0,
                                                        1000, 1,
                                                        2000, 2,
                                                        3000, 3,
                                                        4000, 4 ])
        self.assertEqual (layout.scale_small_ticks_m, [ 0, 0,
                                                        500, 500,
                                                        1000, 1000 ])
