import re
import math
import sys
import cairo
import io
import tile_provider
from units import *
from parsedegrees import *
from cairoutils import *

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

# Returns (xofs, yofs), two floats in [0, tile_size) that are the
# offsets within the tile that contains the given (lat, lon) pair.
# For example, coordinates that would fall exactly in the
# middle of a 512-pixel tile would yield (256, 256).
#
def offsets_within_tile (tile_size, zoom, lat, lon):
    (tile_x, tile_y) = coordinates_to_tile_number (zoom, lat, lon)
    (tile_north, tile_west) = tile_number_to_coordinates (zoom, tile_x, tile_y)
    (tile_south, tile_east) = tile_number_to_coordinates (zoom, tile_x + 1, tile_y + 1)

    xofs = tile_size * (lon - tile_west) / (tile_east - tile_west)
    yofs = tile_size * (lat - tile_north) / (tile_south - tile_north)
    return (xofs, yofs)

def compute_real_world_mm_per_tile (latitude, zoom):
    lat_rad = math.radians (latitude)

    circumference_at_equator = 40075016686 # millimeters
    meridian_length = circumference_at_equator * math.cos (lat_rad)
    tiles_around_the_earth = 2 ** zoom

    mm_per_tile = meridian_length / tiles_around_the_earth
    return mm_per_tile

class ChartRenderer:
    def __init__ (self, layout):
        self.map_scale_denom = 50000.0
        self.map_center_coords = (19.4337, -96.8811) # lat, lon
        self.map_width_mm = 0.0
        self.map_height_mm = 0.0
        self.map_size_is_set = False
        self.map_to_left_margin_mm = 0.0
        self.map_to_top_margin_mm = 0.0
        self.north_tile_idx = 0
        self.west_tile_idx = 0
        self.south_tile_idx = 0
        self.east_tile_idx = 0
        self.tile_indexes_are_computed = False

        self.validate_layout (layout)
        self.layout = layout

        self.tile_provider = None

        self.frame_width_mm = 1.5
        self.frame_inner_thickness_pt = 0.5
        self.frame_outer_thickness_pt = 1.0
        self.frame_color_rgb = (0, 0, 0)

    def validate_layout (self, layout):
        zoom = layout.zoom

        if not (type (zoom) == int and zoom >= 0 and zoom <= 19):
            raise ValueError ("Zoom must be an integer in the range [0, 19]")

    def set_map_size_mm (self, width_mm, height_mm):
        self.map_width_mm = width_mm
        self.map_height_mm = height_mm
        self.map_size_is_set = True

    def set_map_to_top_left_margin_mm (self, x_mm, y_mm):
        self.map_to_left_margin_mm = x_mm
        self.map_to_top_margin_mm = y_mm

    def set_map_center_and_scale (self, lat, lon, scale_denom):
        self.map_center_coords = (lat, lon)
        self.map_scale_denom = scale_denom

    def set_tile_provider (self, tile_provider):
        self.tile_provider = tile_provider

    # We need to scale tiles by this much to get them to the final rendered size
    def compute_tile_scale_factor (self, tile_size):
        if not self.map_size_is_set:
            raise Exception ("ChartRenderer.set_map_size_mm() has not been called!")

        tile_width_mm = compute_real_world_mm_per_tile (self.map_center_coords[0], self.layout.zoom) / self.map_scale_denom
        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt

        tile_scale_factor = tile_width_mm / unscaled_tile_mm
        return tile_scale_factor

    def compute_tile_bounds (self, tile_size):
        tile_scale_factor = self.compute_tile_scale_factor (tile_size)

        half_width_mm = self.map_width_mm / 2.0
        half_height_mm = self.map_height_mm / 2.0

        (center_tile_x, center_tile_y) = coordinates_to_tile_number (self.layout.zoom, self.map_center_coords[0], self.map_center_coords[1])

        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt
        scaled_tile_size_mm = unscaled_tile_mm * tile_scale_factor

        half_horizontal_tiles = int (half_width_mm / scaled_tile_size_mm + 1)
        half_vertical_tiles = int (half_height_mm / scaled_tile_size_mm + 1)

        self.north_tile_idx = center_tile_y - half_vertical_tiles
        self.south_tile_idx = center_tile_y + half_vertical_tiles

        self.west_tile_idx = center_tile_x - half_horizontal_tiles
        self.east_tile_idx = center_tile_x + half_horizontal_tiles

        self.tile_indexes_are_computed = True

    # Assumes that the current transformation matrix is set up for millimeters
    def render_to_cairo (self, cr):
        self.render_map_data (cr)
        self.render_map_frame (cr)

    def render_map_frame (self, cr):
        cr.save ()

        set_source_rgb (cr, self.frame_color_rgb)
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

    # Downloads tiles and composites them into a big image surface
    def make_map_surface (self, leftmost_tile, topmost_tile, width_tiles, height_tiles):
        tile_size = self.tile_provider.get_tile_size ()
        map_surf = cairo.ImageSurface (cairo.FORMAT_RGB24, tile_size * width_tiles, tile_size * height_tiles)
        cr = cairo.Context (map_surf)

        tiles_downloaded = 0

        print ("Downloading {0} tiles...".format (width_tiles * height_tiles))

        for y in range (0, height_tiles):
            for x in range (0, width_tiles):
                tile_x = x + leftmost_tile
                tile_y = y + topmost_tile

                tiles_downloaded += 1
                print ("Downloading tile {0}".format(tiles_downloaded), end='\r', flush=True)

                png_data = self.tile_provider.get_tile_png (self.layout.zoom, tile_x, tile_y)
                tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))

                tile_xpos = x * tile_size
                tile_ypos = y * tile_size

                cr.set_source_surface (tile_surf, tile_xpos, tile_ypos)
                cr.paint ()

        print ("")

        return map_surf

    # Returns (xpixels, ypixels), both floats, that correspond to the map_center_coords
    # with respect to the downloaded tiles.
    #
    def center_offsets_within_map (self):
        tile_size = self.tile_provider.get_tile_size ()

        (center_tile_x, center_tile_y) = coordinates_to_tile_number (self.layout.zoom, self.map_center_coords[0], self.map_center_coords[1])
        (center_tile_xofs, center_tile_yofs) = offsets_within_tile (tile_size, self.layout.zoom, self.map_center_coords[0], self.map_center_coords[1])

        map_surface_xofs = (center_tile_x - self.west_tile_idx) * tile_size + center_tile_xofs
        map_surface_yofs = (center_tile_y - self.north_tile_idx) * tile_size + center_tile_yofs

        return (map_surface_xofs, map_surface_yofs)

    def render_map_data (self, cr):
        if self.tile_provider is None:
            print ("No tile provider; generating empty map")
            return

        tile_size = self.tile_provider.get_tile_size ()

        self.compute_tile_bounds (tile_size)

        width_tiles = self.east_tile_idx - self.west_tile_idx + 1
        height_tiles = self.south_tile_idx - self.north_tile_idx + 1

        if width_tiles < 1 or height_tiles < 1:
            raise Exception ("Invalid coordinates; must produce at least 1x1 tiles")

        # Download map image; figure out the offsets within the map for the center point

        map_surface = self.make_map_surface (self.west_tile_idx, self.north_tile_idx, width_tiles, height_tiles)
        # map_surface.write_to_png ("map-surface.png")

        (map_surface_xofs, map_surface_yofs) = self.center_offsets_within_map ()

        # Clip to the frame

        cr.save ()
        self.clip_to_map (cr)

        # Center on the map
        cr.translate (self.map_to_left_margin_mm + self.map_width_mm / 2.0,
                      self.map_to_top_margin_mm + self.map_height_mm / 2.0)

        # Scale the map down to the final size

        scale_factor = self.compute_tile_scale_factor (tile_size)
        cr.scale (scale_factor, scale_factor)

        points_to_mm = pt_to_mm (1.0)
        cr.scale (points_to_mm, points_to_mm)

        # Offset the scaled map so that it is centered.

        cr.translate (-map_surface_xofs, -map_surface_yofs)
        cr.set_source_surface (map_surface)
        cr.paint ()

        cr.restore ()

if __name__ == "__main__":
    chart_renderer = ChartRenderer ()

    chart_renderer.set_paper_size_mm (inch_to_mm (11), inch_to_mm (8.5))
    chart_renderer.set_map_size_mm (inch_to_mm (10.25), inch_to_mm (7.75))
    chart_renderer.set_map_to_top_left_margin_mm (inch_to_mm (0.375), inch_to_mm (0.375))

    chart_renderer.set_tile_provider (tile_provider.MapboxTileProvider ('pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ',
                                                                        'federicomenaquintero',
                                                                        'cil44s8ep000c9jm18x074iwv'))

    chart_renderer.set_map_center_and_scale (19.4621106, -96.9040473, 50000) # Cerro Malinche

    chart_renderer.render_to_svg ("foo.svg")
