import pyproj
import cairo

def inch_to_mm (inch):
    return inch * 25.4

def mm_to_inch (mm):
    return mm / 25.4

def mm_to_pt (mm):
    return mm / 25.4 * 72.0

def pt_to_mm (pt):
    return pt / 72.0 * 25.4

def set_source_rgb(cr, color):
    cr.set_source_rgb (color[0], color[1], color[2])

def rectangle_thickness_outside (cr, x, y, width, height, thickness):
    cr.set_line_join (cairo.LINE_JOIN_MITER)
    cr.set_line_width (thickness)
    cr.rectangle (x - thickness / 2.0,
                  y - thickness / 2.0,
                  width + thickness,
                  height + thickness)
    cr.stroke ()

def rectangle_thickness_inside (cr, x, y, width, height, thickness):
    cr.set_line_join (cairo.LINE_JOIN_MITER)
    cr.set_line_width (thickness)
    cr.rectangle (x + thickness / 2.0,
                  y + thickness / 2.0,
                  width - thickness,
                  height - thickness)
    cr.stroke ()

class ChartRenderer:
    def __init__ (self):
        self.paper_width_mm = 0.0
        self.paper_height_mm = 0.0
        self.map_scale_denom = 50000
        self.upper_left_coords = (0, 0) # lat, lon
        self.lower_right_coords = (0, 0) # computed from upper_left_coords, map_scale_denom, map_{width,height}_mm
        self.map_width_mm = 0.0
        self.map_height_mm = 0.0
        self.map_to_left_margin_mm = 0.0
        self.map_to_top_margin_mm = 0.0

        self.frame_width_mm = 1.5
        self.frame_inner_thickness_pt = 0.5
        self.frame_outer_thickness_pt = 1.0
        self.frame_color_rgb = (0, 0, 0)

    def set_paper_size_mm (self, width_mm, height_mm):
        self.paper_width_mm = width_mm
        self.paper_height_mm = height_mm

    def set_map_size_mm (self, width_mm, height_mm):
        self.map_width_mm = width_mm
        self.map_height_mm = height_mm

    def set_map_to_top_left_margin_mm (self, x_mm, y_mm):
        self.map_to_left_margin_mm = x_mm
        self.map_to_top_margin_mm = y_mm

    def render_to_svg (self, filename):
        surf = cairo.SVGSurface (filename, mm_to_pt (self.paper_width_mm), mm_to_pt (self.paper_height_mm))

        # The SVG surface is created in points, but we want to render everything in millimeters.
        # Set up a scaling transformation and render everything based on that.

        cr = cairo.Context (surf)
        factor = mm_to_pt (1.0)
        cr.scale (factor, factor)

        self.render_to_cairo (cr)
        surf.show_page ()

    def render_to_cairo (self, cr):
        self.render_map_frame (cr)

    def render_map_frame (self, cr):
        cr.save ()

        inner_thickness_mm = pt_to_mm (self.frame_inner_thickness_pt)
        outer_thickness_mm = pt_to_mm (self.frame_outer_thickness_pt)

        rectangle_thickness_outside (cr,
                                     self.map_to_left_margin_mm,
                                     self.map_to_top_margin_mm,
                                     self.map_width_mm,
                                     self.map_height_mm,
                                     inner_thickness_mm)

        rectangle_thickness_inside (cr,
                                    self.map_to_left_margin_mm - self.frame_width_mm,
                                    self.map_to_top_margin_mm - self.frame_width_mm,
                                    self.map_width_mm + 2 * self.frame_width_mm,
                                    self.map_height_mm + 2 * self.frame_width_mm,
                                    outer_thickness_mm)

        cr.restore ()

if __name__ == "__main__":
    chart_renderer = ChartRenderer ()

    chart_renderer.set_paper_size_mm (inch_to_mm (11), inch_to_mm (8.5))
    chart_renderer.set_map_size_mm (inch_to_mm (10), inch_to_mm (7.5))
    chart_renderer.set_map_to_top_left_margin_mm (inch_to_mm (0.5), inch_to_mm (0.5))

    chart_renderer.render_to_svg ("foo.svg")
