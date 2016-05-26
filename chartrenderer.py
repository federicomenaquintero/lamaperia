import re
import math
import sys
import cairo
import io
from tilecoords import *
import tile_provider
import framerenderer
import scalerenderer
from units import *
from parsedegrees import *
from cairoutils import *

class ChartRenderer:
    def __init__ (self, layout):
        self.north_tile_idx = 0
        self.west_tile_idx = 0
        self.south_tile_idx = 0
        self.east_tile_idx = 0
        self.tile_indexes_are_computed = False

        self.validate_layout (layout)
        self.layout = layout

        self.tile_provider = None

    def validate_layout (self, layout):
        zoom = layout.zoom

        if not (type (zoom) == int and zoom >= 0 and zoom <= 19):
            raise ValueError ("Zoom must be an integer in the range [0, 19]")

    def set_tile_provider (self, tile_provider):
        self.tile_provider = tile_provider

    # We need to scale tiles by this much to get them to the final rendered size
    def compute_tile_scale_factor (self, tile_size):
        tile_width_mm = compute_real_world_mm_per_tile (self.layout.center_lat, self.layout.zoom) / self.layout.map_scale_denom
        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt

        tile_scale_factor = tile_width_mm / unscaled_tile_mm
        return tile_scale_factor

    def compute_tile_bounds (self, tile_size):
        tile_scale_factor = self.compute_tile_scale_factor (tile_size)

        half_width_mm = self.layout.map_width_mm / 2.0
        half_height_mm = self.layout.map_height_mm / 2.0

        (center_tile_x, center_tile_y) = coordinates_to_tile_number (self.layout.zoom, self.layout.center_lat, self.layout.center_lon)

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
        if self.layout.draw_map:
            self.render_map_data (cr)

        if self.layout.draw_map_frame:
            self.render_map_frame (cr)

        if self.layout.draw_scale:
            self.render_scale (cr)

    def render_map_frame (self, cr):
        cr.save ()

        frame_renderer = framerenderer.FrameRenderer (self.layout)
        frame_renderer.render (cr)

        cr.restore ()

    def clip_to_map (self, cr):
        cr.rectangle (self.layout.map_to_left_margin_mm, self.layout.map_to_top_margin_mm,
                      self.layout.map_width_mm, self.layout.map_height_mm)
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
        (center_tile_x, center_tile_y) = coordinates_to_tile_and_fraction (self.layout.zoom, self.layout.center_lat, self.layout.center_lon)

        center_tile_x -= self.west_tile_idx
        center_tile_y -= self.north_tile_idx

        tile_size = self.tile_provider.get_tile_size ()

        return (center_tile_x * tile_size, center_tile_y * tile_size)

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
        cr.translate (self.layout.map_to_left_margin_mm + self.layout.map_width_mm / 2.0,
                      self.layout.map_to_top_margin_mm + self.layout.map_height_mm / 2.0)

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

    def render_scale (self, cr):
        cr.save ()

        scale_renderer = scalerenderer.ScaleRenderer (self.layout.map_scale_denom, 5, 1, 100)
        scale_renderer.render (cr, self.layout.scale_xpos_mm, self.layout.scale_ypos_mm)

        cr.restore ()
