import math
from units import *
from cairoutils import *
from gi.repository import Pango

# Converts decimal degrees to arc minutes starting from zero.  For example, arc_minutes (10.5) = 630
# Does not truncate arc seconds, so you'll obtain decimal minutes!
def degrees_to_arc_minutes (decimal_degrees):
    return decimal_degrees * 60

def arc_minutes_to_degrees (arc_minutes):
    return arc_minutes / 60

def fmod_positive (x, y):
    return x - math.floor (x / y) * y

class FrameRenderer:
    def __init__ (self, chart_geometry):
        assert chart_geometry is not None
        self.geometry = chart_geometry

        self.frame_width_mm = 1.5
        self.frame_inner_thickness_pt = 0.5
        self.frame_outer_thickness_pt = 1.0
        self.frame_color_rgb = (0, 0, 0)

    def render_frame (self, cr):
        inner_thickness_mm = pt_to_mm (self.frame_inner_thickness_pt)
        outer_thickness_mm = pt_to_mm (self.frame_outer_thickness_pt)

        map_layout = self.geometry.map_layout

        set_source_rgb (cr, self.frame_color_rgb)

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

    def render_ticks (self, cr):
        map_layout = self.geometry.map_layout

        upper_left_coords = self.geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm,
                                                                        map_layout.map_to_top_margin_mm)

        lower_right_coords = self.geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm + map_layout.map_width_mm,
                                                                         map_layout.map_to_top_margin_mm + map_layout.map_height_mm)

        left_bound_1 = map_layout.map_to_left_margin_mm - self.frame_width_mm
        left_bound_2 = map_layout.map_to_left_margin_mm

        right_bound_1 = map_layout.map_to_left_margin_mm + map_layout.map_width_mm
        right_bound_2 = map_layout.map_to_left_margin_mm + map_layout.map_width_mm + self.frame_width_mm

        top_bound_1 = map_layout.map_to_top_margin_mm - self.frame_width_mm
        top_bound_2 = map_layout.map_to_top_margin_mm

        bottom_bound_1 = map_layout.map_to_top_margin_mm + map_layout.map_height_mm
        bottom_bound_2 = map_layout.map_to_top_margin_mm + map_layout.map_height_mm + self.frame_width_mm

        self.paint_arc_minutes (cr, top_bound_1, top_bound_2, upper_left_coords[0], upper_left_coords[1], lower_right_coords[1], 1, True, True)
        self.paint_arc_minutes (cr, bottom_bound_1, bottom_bound_2, lower_right_coords[0], upper_left_coords[1], lower_right_coords[1], 1, True, False)

        self.paint_arc_minutes (cr, left_bound_1, left_bound_2, upper_left_coords[1], upper_left_coords[0], lower_right_coords[0], 1, False, True)
        self.paint_arc_minutes (cr, right_bound_1, right_bound_2, lower_right_coords[1], upper_left_coords[0], lower_right_coords[0], 1, False, False)

    # Creates an array of values:
    #   [ start_coord, x1, x2, x3, ..., end_coord ]
    # such that the xN are evenly spaced at integer multiples of every_arc_minutes.
    #
    def generate_ticks (self, start_coord, end_coord, every_arc_minutes):
        start_mins = degrees_to_arc_minutes (start_coord)
        end_mins = degrees_to_arc_minutes (end_coord)

        ticks = [ start_coord ]

        first_m = start_mins - fmod_positive (start_mins, every_arc_minutes) + every_arc_minutes

        m = first_m
        i = 1

        while m < end_mins:
            ticks.append (arc_minutes_to_degrees (m))
            m = first_m + i * every_arc_minutes
            i += 1

        ticks.append (end_coord)

        return ticks

    def paint_arc_minutes (self, cr, bound1_mm, bound2_mm, along_edge_coord, start_coord, end_coord, every_arc_minutes, is_horizontal, labels_above):
        start = min (start_coord, end_coord)
        end = max (start_coord, end_coord)

        ticks = self.generate_ticks (start, end, every_arc_minutes)
        ticks_mm = []

        for i in range (len (ticks)):
            c = ticks[i]
            if is_horizontal:
                (mm, dummy) = self.geometry.transform_lat_lon_to_page_mm (along_edge_coord, c)
            else:
                (dummy, mm) = self.geometry.transform_lat_lon_to_page_mm (c, along_edge_coord)

            ticks_mm.append (mm)

        for i in range (len (ticks_mm) - 1):
            start = ticks_mm[i]
            end   = ticks_mm[i + 1]

            if i % 2 == 0:
                if is_horizontal:
                    x = start
                    y = bound1_mm
                    w = end - start
                    h = bound2_mm - bound1_mm
                else:
                    x = bound1_mm
                    y = start
                    w = bound2_mm - bound1_mm
                    h = end - start

                cr.rectangle (x, y, w, h)
                cr.fill ()

        if labels_above:
            fixed_anchor_coord = bound1_mm
            if is_horizontal:
                anchor = "s"
            else:
                anchor = "e"
        else:
            fixed_anchor_coord = bound2_mm
            if is_horizontal:
                anchor = "n"
            else:
                anchor = "w"

        fd = Pango.font_description_from_string ("Luxi Serif 6")

        for i in range (len (ticks_mm)):
            c = ticks[i]
            if fmod_positive (degrees_to_arc_minutes (c), every_arc_minutes) < 0.000001:
                mm = ticks_mm[i]
                (minutes, degrees) = math.modf (c)
                minutes = int (math.fabs (minutes) * 60 + 0.5)
                degrees = int (degrees)
                if minutes % 5 == 0:
                    if is_horizontal:
                        render_text (cr, mm, fixed_anchor_coord, anchor, fd, "{0}°{1:02d}'".format (degrees, minutes))
                    else:
                        render_text (cr, fixed_anchor_coord, mm, anchor, fd, "{0}°{1:02d}'".format (degrees, minutes))
