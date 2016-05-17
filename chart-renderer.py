import math
import sys
import pyproj
import cairo
import io
import tile_provider

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

# Parses a string that represents either decimal or sexagesimal
# degrees into a decimal degrees value.  Returns None if invalid.
#
# Valid strings:
#    decimal degrees: -19.234    25.6  (just a regular float number without exponents)
#
#    sexagesimal degrees:
#    15d
#    15d30m
#    15d30m6s
#    all the above can be negative as well.  All need to end in either of d/m/s.

def parse_degrees (value):
    decimal_re = re.compile (r"^[-+]?\d*\.?\d+$")
    if decimal_re.match (value):
        return float(value)

    sexagesimal_re = re.compile (r"^([-+]?\d+)d((\d+)m((\d+)s)?)?$")
    m = sexagesimal_re.match (value)

    if m == None:
        return None

    (deg, min, sec) = m.group (1, 3, 5)

    deg = float (deg)

    if min == None:
        min = 0.0
    else:
        min = float(min)

    if sec == None:
        sec = 0.0
    else:
        sec = float(sec)

    decimals = min / 60.0 + sec / 3600.0

    if deg < 0:
        return deg - decimals
    else:
        return deg + decimals

# stolen from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#
# returns (x, y) pair
def coordinates_to_tile_number (z, lat, lon):
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = int ((lon + 180.0) / 360.0 * n)
    ytile = int ((1.0 - math.log (math.tan (lat_rad) + (1 / math.cos (lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def tile_number_to_coordinates (z, xtile, ytile):
    n = 2.0 ** z
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = lat_rad * 180.0 / math.pi
    return (lat_deg, lon_deg)

def compute_real_world_mm_per_tile (latitude, zoom):
    lat_rad = math.radians (latitude)

    circumference_at_equator = 40075016686 # millimeters
    meridian_length = circumference_at_equator * math.cos (lat_rad)
    tiles_around_the_earth = 2 ** zoom

    mm_per_tile = meridian_length / tiles_around_the_earth
    return mm_per_tile

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
        self.map_scale_denom = 50000.0
        self.map_center_coords = (19.4337, -96.8811) # lat, lon
        self.upper_left_coords = (0, 0) # lat, lon
        self.lower_right_coords = (0, 0) # computed from upper_left_coords, map_scale_denom, map_{width,height}_mm
        self.map_width_mm = 0.0
        self.map_height_mm = 0.0
        self.map_size_is_set = False
        self.map_to_left_margin_mm = 0.0
        self.map_to_top_margin_mm = 0.0
        self.bounds_are_computed = False

        self.zoom = 15

        self.tile_provider = None

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
        self.map_size_is_set = True

    def set_map_to_top_left_margin_mm (self, x_mm, y_mm):
        self.map_to_left_margin_mm = x_mm
        self.map_to_top_margin_mm = y_mm

    def set_zoom (self, zoom):
        if not (type (zoom) == int and type >= 0 and type <= 19):
            raise ValueError ("Zoom must be an integer in the range [0, 19]")

        self.zoom = zoom

    def set_map_center_and_scale (self, lat, lon, scale_denom):
        self.map_center_coords = (lat, lon)
        self.map_scale_denom = scale_denom

    def set_tile_provider (self, tile_provider):
        self.tile_provider = tile_provider

    def set_map_upper_left_coords (self, lat, lon):
        self.upper_left_coords = (lat, lon)

    # We need to scale tiles by this much to get them to the final rendered size
    def compute_tile_scale_factor (self, tile_size):
        if not self.map_size_is_set:
            raise Exception ("ChartRenderer.set_map_size_mm() has not been called!")

        tile_width_mm = compute_real_world_mm_per_tile (self.map_center_coords[0], self.zoom) / self.map_scale_denom
        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt

        tile_scale_factor = tile_width_mm / unscaled_tile_mm
        return tile_scale_factor

    def render_to_svg (self, filename):
        surf = cairo.SVGSurface (filename, mm_to_pt (self.paper_width_mm), mm_to_pt (self.paper_height_mm))

        # The SVG surface is created in points, but we want to render everything in millimeters.
        # Set up a scaling transformation and render everything based on that.

        cr = cairo.Context (surf)
        factor = mm_to_pt (1.0)
        cr.scale (factor, factor)

        self.render_to_cairo (cr)
        surf.show_page ()

    # Assumes that the current transformation matrix is set up for millimeters
    def render_to_cairo (self, cr):
        self.render_map_frame (cr)
        self.render_map_data (cr)

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

    def clip_to_map (self, cr):
        cr.rectangle (self.map_to_left_margin_mm, self.map_to_top_margin_mm,
                      self.map_width_mm, self.map_height_mm)
        cr.clip ()

    def make_map_surface (self, leftmost_tile, topmost_tile, width_tiles, height_tiles):
        have_tile_surf = False
        tile_size = 0
        map_surf = None
        cr = None
        tiles_downloaded = 0

        print ("Downloading {0} tiles...".format (width_tiles * height_tiles))

        for y in range (0, height_tiles):
            for x in range (0, width_tiles):
                tile_x = x + leftmost_tile
                tile_y = y + topmost_tile

                tiles_downloaded += 1
                print ("Downloading tile {0}".format(tiles_downloaded), end='\r', flush=True)

                png_data = self.tile_provider.get_tile_png (self.zoom, tile_x, tile_y)
                tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))

                if not have_tile_size:
                    have_tile_size = True
                    tile_size = tile_surf.get_width ()
                    map_surf = cairo.ImageSurface (cairo.FORMAT_RGB24, tile_size * width_tiles, tile_size * height_tiles)
                    cr = cairo.Context (map_surf)

                tile_xpos = x * tile_size
                tile_ypos = y * tile_size

                cr.set_source_surface (tile_surf, tile_xpos, tile_ypos)
                cr.paint ()

        print ("")

        return (map_surf, width_tiles * tile_size, height_tiles * tile_size)

    def render_map_data (self, cr):
        (leftmost_tile, topmost_tile) = coordinates_to_tile_number (self.zoom, self.upper_left_coords[0], self.upper_left_coords[1])
        (rightmost_tile, bottommost_tile) = coordinates_to_tile_number (self.zoom, self.lower_right_coords[0], self.lower_right_coords[1])

        width_tiles = rightmost_tile - leftmost_tile + 1
        height_tiles = bottommost_tile - topmost_tile + 1

        if width_tiles < 1 or height_tiles < 1:
            raise Exception ("Invalid coordinates; must produce at least 1x1 tiles")

        if self.tile_provider is None:
            print ("No tile provider; generating empty map")
            return

        (map_surface, map_width, map_height) = self.make_map_surface (leftmost_tile, topmost_tile, width_tiles, height_tiles)

        cr.save ()
        self.clip_to_map (cr)

        cr.move_to (self.map_to_left_margin_mm, self.map_to_top_margin_mm)

        top_left_coords = tile_number_to_coordinates (self.zoom, leftmost_tile, topmost_tile)
        bottom_right_coords = tile_number_to_coordinates (self.zoom, leftmost_tile + width_tiles, topmost_tile + height_tiles)

        map_width_longitude = math.fabs (bottom_right_coords[1] - top_left_coords[1])
        map_height_latitude = math.fabs (bottom_right_coords[0] - top_left_coords[0])

        final_width_longitude = math.fabs (self.lower_right_coords[1] - self.upper_left_coords[1])
        final_height_latitude = math.fabs (self.lower_right_coords[0] - self.upper_left_coords[0])

        cr.scale (self.map_width_mm * map_width_longitude / final_width_longitude,
                  self.map_height_mm * map_height_latitude / final_height_latitude)
        cr.moveto (top_left_coords[1] - self.upper_left_coords[1], top_left_coords[0] - self.upper_left_coords[0])

        cr.set_source_surface (map_surface)
        cr.paint ()

        cr.restore ()

if __name__ == "__main__":
    chart_renderer = ChartRenderer ()

    chart_renderer.set_paper_size_mm (inch_to_mm (19), inch_to_mm (13))
    chart_renderer.set_map_size_mm (inch_to_mm (18), inch_to_mm (12))
    chart_renderer.set_map_to_top_left_margin_mm (inch_to_mm (0.5), inch_to_mm (0.5))

    chart_renderer.compute_corner_coordinates (512)
    sys.exit (0)

    chart_renderer.set_tile_provider (tile_provider.MapboxTileProvider ('pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ',
                                                                        'federicomenaquintero',
                                                                        'cil44s8ep000c9jm18x074iwv'))

    chart_renderer.set_map_upper_left_coords (parse_degrees ("19d30m"), parse_degrees ("-97d"))

    chart_renderer.render_to_svg ("foo.svg")
