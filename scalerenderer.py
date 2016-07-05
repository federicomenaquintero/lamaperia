import cairo
import json
import maplayout
from units import *
from cairoutils import *
from gi.repository import Pango
from gi.repository import PangoCairo

large_ticks_for_50000 = [ (0, 0),
                          (1, 1000),
                          (2, 2000),
                          (3, 3000),
                          (4, 4000) ]
small_ticks_for_50000 = [ (0, 0),
                          (500, 500),
                          (1000, 1000) ]

large_ticks_for_20000 = [ (0, 0),
                          (500, 500),
                          (1000, 1000),
                          (1500, 1500) ]
small_ticks_for_20000 = [ (0, 0),
                          (100, 100),
                          (200, 200),
                          (300, 300),
                          (400, 400),
                          (500, 500) ]

class ScaleRenderer:
    def __init__ (self, map_layout):
        self.map_layout = map_layout

        self.outline_thickness_pt = 0.5
        self.color_rgb = (0, 0, 0)
        self.rule_width_mm = 2.0
        self.tick_length_mm = 0.5

        self.font_description_str = "Luxi Serif 6"
        self.font_description = Pango.font_description_from_string (self.font_description_str)

    def render_alternate_divisions (self, cr, num_divisions, left, top, division_length, division_height):
        half_height = division_height / 2.0

        for i in range (num_divisions):
            if i % 2 == 0:
                y = top
            else:
                y = top + half_height

            x = left + i * division_length

            cr.rectangle (x, y, division_length, half_height)
            cr.fill ()

    def render_ticks (self, cr,
                      xpos, ypos, height,
                      text_anchor,
                      sign,
                      ticks_pairs):
        i = 0

        y1 = ypos
        y2 = ypos + height

        while i < len (ticks_pairs):
            (meters, label) = (ticks_pairs[i], ticks_pairs[i + 1])

            x = xpos + sign * meters * 1000 / self.map_layout.map_scale_denom

            cr.move_to (x, y1)
            cr.line_to (x, y2)
            cr.stroke ()

            render_text (cr, x, y2, text_anchor, self.font_description, "{0}".format (label))

            i += 2

    # The anchor point is the horizontal center of the scale rule,
    # and the vertical top of the scale rule.
    #
    def render (self, cr, center_x, top_y):
        cr.save ()

        layout = self.map_layout

        millimeters_total = (layout.scale_large_divisions_interval_m * layout.scale_num_large_divisions
                             + layout.scale_small_divisions_interval_m * layout.scale_num_small_divisions) * 1000
        rule_length_mm = millimeters_total / layout.map_scale_denom

        # upper-left coords will be (leftmost_x, top_y)
        # size of rule will be (rule_length_mm, self.rule_width_mm)
        leftmost_x = center_x - rule_length_mm / 2.0
        large_scale_x = leftmost_x + layout.scale_num_small_divisions * layout.scale_small_divisions_interval_m * 1000 / layout.map_scale_denom

        # Paint the main outline

        set_source_rgb (cr, self.color_rgb)

        cr.rectangle (leftmost_x, top_y,
                      rule_length_mm, self.rule_width_mm)

        thickness_mm = pt_to_mm (self.outline_thickness_pt)
        cr.set_line_width (thickness_mm)

        cr.set_line_join (cairo.LINE_JOIN_MITER)
        cr.stroke ()

        # Paint the large-scale divisions on the right
        self.render_alternate_divisions (cr,
                                         layout.scale_num_large_divisions,
                                         large_scale_x, top_y,
                                         layout.scale_large_divisions_interval_m * 1000 / layout.map_scale_denom,
                                         self.rule_width_mm)

        self.render_ticks (cr,
                           large_scale_x, top_y + self.rule_width_mm, self.tick_length_mm,
                           "nw",
                           1,
                           layout.scale_large_ticks_m)

        # Paint the small-scale divisions on the left
        self.render_alternate_divisions (cr,
                                         layout.scale_num_small_divisions,
                                         leftmost_x, top_y,
                                         layout.scale_small_divisions_interval_m * 1000 / layout.map_scale_denom,
                                         self.rule_width_mm)

        self.render_ticks (cr,
                           large_scale_x, top_y, -self.tick_length_mm,
                           "sw",
                           -1,
                           layout.scale_small_ticks_m)

        cr.restore ()

if __name__ == "__main__":
    surface = cairo.SVGSurface ("scale.svg", mm_to_pt (inch_to_mm (11.0)), mm_to_pt (inch_to_mm (8.5)))
    cr = cairo.Context (surface)

    factor = mm_to_pt (1.0)
    cr.scale (factor, factor)

    layout = maplayout.MapLayout ()
    layout.load_from_json (json.loads ("""
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
    """))

    scale_renderer = ScaleRenderer (layout)
    scale_renderer.render (cr, inch_to_mm (5.5), inch_to_mm (4))

    font_desc = Pango.font_description_from_string ("Luxi Serif 6")

    render_text (cr, inch_to_mm (5.5), inch_to_mm (4), "s", font_desc, "Hola mundo")
