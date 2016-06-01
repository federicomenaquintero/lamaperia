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
import testutils
import maplayout
import tile_provider
import chartgeometry

class ChartRenderer:
    def __init__ (self, chart_geometry):
        assert chart_geometry is not None
        self.geometry = chart_geometry

        self.map_layout = chart_geometry.map_layout

    # Assumes that the current transformation matrix is set up for millimeters
    def render_to_cairo (self, cr):
        self.geometry.compute_extents_of_downloaded_tiles ()

        if self.map_layout.draw_map:
            self.render_map_data (cr)

        self.render_map_frame (cr)

        if self.map_layout.draw_scale:
            self.render_scale (cr)

    def render_map_frame (self, cr):
        cr.save ()

        frame_renderer = framerenderer.FrameRenderer (self.geometry)

        if self.map_layout.draw_map_frame:
            frame_renderer.render_frame (cr)

        if self.map_layout.draw_ticks:
            frame_renderer.render_ticks (cr)

        cr.restore ()

    def clip_to_map (self, cr):
        cr.rectangle (self.map_layout.map_to_left_margin_mm, self.map_layout.map_to_top_margin_mm,
                      self.map_layout.map_width_mm, self.map_layout.map_height_mm)
        cr.clip ()

    # Downloads tiles and composites them into a big image surface
    def make_map_surface (self):
        geometry = self.geometry
        provider = geometry.tile_provider

        width_tiles = geometry.east_tile_idx - geometry.west_tile_idx + 1
        height_tiles = geometry.south_tile_idx - geometry.north_tile_idx + 1

        assert width_tiles >= 1
        assert height_tiles >= 1

        tile_size = provider.get_tile_size ()
        map_surf = cairo.ImageSurface (cairo.FORMAT_RGB24, tile_size * width_tiles, tile_size * height_tiles)
        cr = cairo.Context (map_surf)

        tiles_downloaded = 0

        print ("Downloading {0} tiles...".format (width_tiles * height_tiles))

        for y in range (0, height_tiles):
            for x in range (0, width_tiles):
                tile_x = x + geometry.west_tile_idx
                tile_y = y + geometry.north_tile_idx

                tiles_downloaded += 1
                print ("Downloading tile {0}".format(tiles_downloaded), end='\r', flush=True)

                png_data = provider.get_tile_png (self.map_layout.zoom, tile_x, tile_y)
                tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))

                tile_xpos = x * tile_size
                tile_ypos = y * tile_size

                cr.set_source_surface (tile_surf, tile_xpos, tile_ypos)
                cr.paint ()

                del tile_surf

        print ("")

        return map_surf

    def render_map_data (self, cr):
        cr.save ()

        map_surface = self.make_map_surface ()
        # map_surface.write_to_png ("map-surface.png") # Uncomment this if you want to examine the downloaded map image

        self.clip_to_map (cr)

        matrix = self.geometry.compute_matrix_from_page_mm_to_map_surface_coordinates ()
        matrix.invert ()
        cr.transform (matrix)
        cr.set_source_surface (map_surface)
        cr.paint ()

        cr.restore ()

    def render_scale (self, cr):
        scale_renderer = scalerenderer.ScaleRenderer (self.map_layout)
        scale_renderer.render (cr, self.map_layout.scale_xpos_mm, self.map_layout.scale_ypos_mm)

#################### tests ####################

class TestChartRenderer (testutils.TestCaseHelper):
    def make_test_map_layout (self):
        layout = maplayout.MapLayout ()
        layout.parse_json ("""
            {
                "paper-width"  : "11 in",
                "paper-height" : "8.5 in",

                "zoom" : 15,

                "center-lat" : 19.4621106,
                "center-lon" : -96.9040473,
                "map-scale"  : 50000,

                "map-width"  : "10 in",
                "map-height" : "7.375 in",
                "map-to-left-margin" : "0.5 in",
                "map-to-top-margin" : "0.375 in"
            }
        """)

        return layout

    def test_downloaded_image_has_correct_size (self):
        map_layout = self.make_test_map_layout ()
        provider = tile_provider.NullTileProvider ()
        geometry = chartgeometry.ChartGeometry (map_layout, provider)

        chart_renderer = ChartRenderer (geometry)

        geometry.compute_extents_of_downloaded_tiles ()

        map_surface = chart_renderer.make_map_surface ()

        # The following tile indices are in TestChartGeometry.test_computes_minimal_extents_of_downloaded_tiles()

        self.assertEqual (map_surface.get_width (),
                          provider.get_tile_size () * (7569 - 7558 + 1))
        self.assertEqual (map_surface.get_height (),
                          provider.get_tile_size () * (14581 - 14573 + 1))

    def test_downloads_the_correct_range_of_tiles (self):
        map_layout = self.make_test_map_layout ()
        provider = tile_provider.NullTileProvider ()
        geometry = chartgeometry.ChartGeometry (map_layout, provider)

        chart_renderer = ChartRenderer (geometry)

        geometry.compute_extents_of_downloaded_tiles ()
        chart_renderer.make_map_surface ()

        self.assertEqual (provider.west_tile_requested_limit, 7558)
        self.assertEqual (provider.north_tile_requested_limit, 14573)
        self.assertEqual (provider.east_tile_requested_limit, 7569)
        self.assertEqual (provider.south_tile_requested_limit, 14581)
