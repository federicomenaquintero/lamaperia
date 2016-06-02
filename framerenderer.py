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

        self.paint_horizontal_arc_minutes (cr, top_bound_1, top_bound_2, upper_left_coords[0], upper_left_coords[1], lower_right_coords[1], 1, True)
        self.paint_horizontal_arc_minutes (cr, bottom_bound_1, bottom_bound_2, lower_right_coords[0], upper_left_coords[1], lower_right_coords[1], 1, False)

        self.paint_vertical_arc_minutes (cr, left_bound_1, left_bound_2, upper_left_coords[1], upper_left_coords[0], lower_right_coords[0], 1, True)
        self.paint_vertical_arc_minutes (cr, right_bound_1, right_bound_2, lower_right_coords[1], upper_left_coords[0], lower_right_coords[0], 1, False)

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

    def paint_horizontal_arc_minutes (self, cr, top_mm, bottom_mm, lat, left_lon, right_lon, every_arc_minutes, labels_above):
        ticks = self.generate_ticks (left_lon, right_lon, every_arc_minutes)
        ticks_mm = []

        for i in range (len (ticks)):
            lon = ticks[i]
            (mm, dummy) = self.geometry.transform_lat_lon_to_page_mm (lat, lon)
            ticks_mm.append (mm)

        for i in range (len (ticks_mm) - 1):
            left = ticks_mm[i]
            right = ticks_mm[i + 1]

            if i % 2 == 0:
                cr.rectangle (left, top_mm, right - left, bottom_mm - top_mm)
                cr.fill ()

        if labels_above:
            y = top_mm
            anchor = "s"
        else:
            y = bottom_mm
            anchor = "n"

        fd = Pango.font_description_from_string ("Luxi Serif 6")

        for i in range (len (ticks_mm)):
            lon = ticks[i]
            if fmod_positive (degrees_to_arc_minutes (lon), every_arc_minutes) < 0.000001:
                x = ticks_mm[i]
                (minutes, degrees) = math.modf (lon)
                minutes = int (math.fabs (minutes) * 60 + 0.5)
                degrees = int (degrees)
                if minutes % 5 == 0:
                    render_text (cr, x, y, anchor, fd, "{0}°{1:02d}'".format (degrees, minutes))

    def paint_vertical_arc_minutes (self, cr, left_mm, right_mm, lon, top_lat, bottom_lat, every_arc_minutes, labels_left):
        ticks = self.generate_ticks (bottom_lat, top_lat, every_arc_minutes)
        ticks.reverse ()
        ticks_mm = []

        for i in range (len (ticks)):
            lat = ticks[i]
            (dummy, mm) = self.geometry.transform_lat_lon_to_page_mm (lat, lon)
            ticks_mm.append (mm)

        for i in range (len (ticks_mm) - 1):
            top = ticks_mm[i]
            bottom = ticks_mm[i + 1]

            if i % 2 == 0:
                cr.rectangle (left_mm, top, right_mm - left_mm, bottom - top)
                cr.fill ()

        if labels_left:
            x = left_mm
            anchor = "e"
        else:
            x = right_mm
            anchor = "w"

        fd = Pango.font_description_from_string ("Luxi Serif 6")

        for i in range (len (ticks_mm)):
            lat = ticks[i]
            if fmod_positive (degrees_to_arc_minutes (lat), every_arc_minutes) < 0.000001:
                y = ticks_mm[i]
                (minutes, degrees) = math.modf (lat)
                minutes = int (math.fabs (minutes) * 60 + 0.5)
                degrees = int (degrees)
                if minutes % 5 == 0:
                    render_text (cr, x, y, anchor, fd, "{0}°{1:02d}'".format (degrees, minutes))
