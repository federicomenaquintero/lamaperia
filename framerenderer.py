import math
from units import *
from cairoutils import *

# Converts decimal degrees to arc minutes starting from zero.  For example, arc_minutes (10.5) = 630
# Does not truncate arc seconds, so you'll obtain decimal minutes!
def arc_minutes (decimal_degrees):
    return decimal_degrees * 60

class FrameRenderer:
    def __init__ (self, chart_geometry):
        assert chart_geometry is not None
        self.geometry = chart_geometry

        self.frame_width_mm = 1.5
        self.frame_inner_thickness_pt = 0.5
        self.frame_outer_thickness_pt = 1.0
        self.frame_color_rgb = (0, 0, 0)

    def render (self, cr):
        set_source_rgb (cr, self.frame_color_rgb)
        inner_thickness_mm = pt_to_mm (self.frame_inner_thickness_pt)
        outer_thickness_mm = pt_to_mm (self.frame_outer_thickness_pt)

        map_layout = self.geometry.map_layout

        rectangle_thickness_outside (cr,
                                     map_layout.map_to_left_margin_mm,
                                     map_layout.map_to_top_margin_mm,
                                     map_layout.map_width_mm,
                                     map_layout.map_height_mm,
                                     inner_thickness_mm)

        rectangle_thickness_inside (cr,
                                    map_layout.map_to_left_margin_mm - self.frame_width_mm,
                                    map_layout.map_to_top_margin_mm - self.frame_width_mm,
                                    map_layout.map_width_mm + 2 * self.frame_width_mm,
                                    map_layout.map_height_mm + 2 * self.frame_width_mm,
                                    outer_thickness_mm)
