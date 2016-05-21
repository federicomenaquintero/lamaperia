import cairo
from cairoutils import *
from gi.repository import Pango
from gi.repository import PangoCairo

def inch_to_mm (inch):
    return inch * 25.4

def mm_to_inch (mm):
    return mm / 25.4

def mm_to_pt (mm):
    return mm / 25.4 * 72.0

def pt_to_mm (pt):
    return pt / 72.0 * 25.4

class ScaleRenderer:
    def __init__ (self, map_scale_denom, kilometers_total, kilometers_with_small_scale, small_scale_meters):
        self.map_scale_denom = map_scale_denom
        self.outline_thickness_pt = 0.5
        self.color_rgb = (0, 0, 0)
        self.rule_width_mm = 2.5
        self.kilometers_total = 5
        self.kilometers_with_small_scale = kilometers_with_small_scale
        self.small_scale_meters = small_scale_meters

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

    # The anchor point is the horizontal center of the scale rule,
    # and the vertical top of the scale rule.
    #
    def render (self, cr, center_x, top_y):
        millimeters_total = self.kilometers_total * 1000000
        rule_length_mm = millimeters_total / self.map_scale_denom
        mm_per_kilometer = rule_length_mm / self.kilometers_total

        # upper-left coords will be (leftmost_x, top_y)
        # size of rule will be (rule_length_mm, self.rule_width_mm)
        leftmost_x = center_x - rule_length_mm / 2.0

        # Paint the main outline

        set_source_rgb (cr, self.color_rgb)

        cr.rectangle (leftmost_x, top_y,
                      rule_length_mm, self.rule_width_mm)

        thickness_mm = pt_to_mm (self.outline_thickness_pt)
        cr.set_line_width (thickness_mm)

        cr.set_line_join (cairo.LINE_JOIN_MITER)
        cr.stroke ()

        # Paint the main divisions on the right
        self.render_alternate_divisions (cr,
                                         self.kilometers_total - self.kilometers_with_small_scale,
                                         leftmost_x + mm_per_kilometer * self.kilometers_with_small_scale, top_y,
                                         mm_per_kilometer, self.rule_width_mm)

        # Paint the small-scale divisions on the left
        self.render_alternate_divisions (cr,
                                         self.kilometers_with_small_scale * 1000 // self.small_scale_meters,
                                         leftmost_x, top_y,
                                         mm_per_kilometer * self.small_scale_meters / (self.kilometers_with_small_scale * 1000), self.rule_width_mm)

if __name__ == "__main__":
    surface = cairo.PDFSurface ("scale.pdf", mm_to_pt (inch_to_mm (11.0)), mm_to_pt (inch_to_mm (8.5)))
    cr = cairo.Context (surface)

    factor = mm_to_pt (1.0)
    cr.scale (factor, factor)

    scale_renderer = ScaleRenderer (50000, 5, 1, 100)
    scale_renderer.render (cr, inch_to_mm (5.5), inch_to_mm (4))

    layout = PangoCairo.create_layout (cr)
    layout.set_font_description (Pango.font_description_from_string ("Luxi Serif 6"))
    layout.set_text ("Hola mundo", -1)

    cr.move_to (inch_to_mm (5.5), inch_to_mm (4))
    cr.scale (pt_to_mm (1), pt_to_mm (1))

    (ink_rect, logical_rect) = layout.get_pixel_extents ()
    (x, y) = cr.get_current_point ()
    cr.move_to (x - logical_rect.width / 2, y - logical_rect.height)
    PangoCairo.show_layout (cr, layout)

    surface.show_page ()
