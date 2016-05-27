import math
import cairo
from tilecoords import *
import tile_provider
from units import *
import testutils
import maplayout
import tile_provider

class ChartGeometry:
    def __init__ (self, map_layout, tile_provider):
        assert map_layout is not None
        assert tile_provider is not None

        self.map_layout = map_layout

        self.north_tile_idx = 0
        self.west_tile_idx = 0
        self.south_tile_idx = 0
        self.east_tile_idx = 0
        self.tile_indexes_are_computed = False

        self.tile_provider = tile_provider

    # We need to scale tiles by this much to get them to the final rendered size
    def compute_tile_scale_factor (self):
        tile_size = self.tile_provider.get_tile_size ()

        tile_width_mm = compute_real_world_mm_per_tile (self.map_layout.center_lat, self.map_layout.zoom) / self.map_layout.map_scale_denom
        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt

        tile_scale_factor = tile_width_mm / unscaled_tile_mm
        return tile_scale_factor

    def compute_extents_of_downloaded_tiles (self):
        if self.tile_provider is None:
            raise Exception ("Cannot compute_extents_of_downloaded_tiles() without a tile_provider!  Call set_tile_provider() first!")

        tile_size = self.tile_provider.get_tile_size ()

        tile_scale_factor = self.compute_tile_scale_factor ()

        half_width_mm = self.map_layout.map_width_mm / 2.0
        half_height_mm = self.map_layout.map_height_mm / 2.0

        (center_tile_x, center_tile_y) = coordinates_to_tile_and_fraction (self.map_layout.zoom, self.map_layout.center_lat, self.map_layout.center_lon)

        unscaled_tile_mm = pt_to_mm (tile_size) # image surfaces get loaded at 1 px -> 1 pt
        scaled_tile_size_mm = unscaled_tile_mm * tile_scale_factor

        half_horizontal_tiles = half_width_mm / scaled_tile_size_mm
        half_vertical_tiles   = half_height_mm / scaled_tile_size_mm

        self.north_tile_idx = int (center_tile_y - half_vertical_tiles)
        self.south_tile_idx = int (center_tile_y + half_vertical_tiles)

        self.west_tile_idx = int (center_tile_x - half_horizontal_tiles)
        self.east_tile_idx = int (center_tile_x + half_horizontal_tiles)

        if self.west_tile_idx > self.east_tile_idx or self.north_tile_idx > self.south_tile_idx:
            raise Exception ("Invalid coordinates; must produce at least 1x1 tiles")

        self.tile_indexes_are_computed = True

    # Returns (xpixels, ypixels), both floats, that correspond to the map_center_coords
    # with respect to the downloaded tiles.
    #
    def center_offsets_within_map (self):
        assert self.tile_indexes_are_computed

        (center_tile_x, center_tile_y) = coordinates_to_tile_and_fraction (self.map_layout.zoom, self.map_layout.center_lat, self.map_layout.center_lon)

        center_tile_x -= self.west_tile_idx
        center_tile_y -= self.north_tile_idx

        tile_size = self.tile_provider.get_tile_size ()

        return (center_tile_x * tile_size, center_tile_y * tile_size)

    # If we start with a CTM so that (0, 0) is at the page's top-left corner,
    # and 1 unit is 1 mm, this computes a transformation matrix to get
    # from there to map coordinates:  (0, 0) will be at the north-west
    # corner of the downloaded tiles, and 1 unit will be 1 pixel in the tiles.
    #
    def compute_matrix_from_page_mm_to_map_surface_coordinates (self):
        m = cairo.Matrix () # starts with a unit matrix

        # Center on the map
        m.translate (self.map_layout.map_to_left_margin_mm + self.map_layout.map_width_mm / 2.0,
                     self.map_layout.map_to_top_margin_mm + self.map_layout.map_height_mm / 2.0)

        # Scale the map down to the final size

        tile_size = self.tile_provider.get_tile_size ()

        scale_factor = self.compute_tile_scale_factor ()
        m.scale (scale_factor, scale_factor)

        points_to_mm = pt_to_mm (1.0)
        m.scale (points_to_mm, points_to_mm)

        # Offset the scaled map so that it is centered.

        (map_surface_xofs, map_surface_yofs) = self.center_offsets_within_map ()
        m.translate (-map_surface_xofs, -map_surface_yofs)

        m.invert ()
        return m

    def transform_page_mm_to_lat_lon (self, page_x, page_y):
        matrix = self.compute_matrix_from_page_mm_to_map_surface_coordinates ()

        (pixel_x, pixel_y) = matrix.transform_point (page_x, page_y)

        tile_size = self.tile_provider.get_tile_size ()

        global_pixel_x = self.west_tile_idx + pixel_x / tile_size
        global_pixel_y = self.north_tile_idx + pixel_y / tile_size

        return tile_number_to_coordinates (self.map_layout.zoom, global_pixel_x, global_pixel_y)

#################### tests ####################

class TestChartGeometry (testutils.TestCaseHelper):
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

    def test_computes_minimal_extents_of_downloaded_tiles (self):
        map_layout = self.make_test_map_layout ()
        provider = tile_provider.NullTileProvider ()
        chart_geometry = ChartGeometry (map_layout, provider)

        chart_geometry.compute_extents_of_downloaded_tiles ()

        # We know these to be correct; these is the minimal rectangle of tiles that spans the test area
        self.assertEqual (chart_geometry.west_tile_idx, 7558)
        self.assertEqual (chart_geometry.north_tile_idx, 14573)
        self.assertEqual (chart_geometry.east_tile_idx, 7569)
        self.assertEqual (chart_geometry.south_tile_idx, 14581)

    def test_configuration_has_map_center_in_the_correct_transformed_coordinates (self):
        map_layout = self.make_test_map_layout ()
        provider = tile_provider.NullTileProvider ()
        chart_geometry = ChartGeometry (map_layout, provider)

        chart_geometry.compute_extents_of_downloaded_tiles ()

        # Figure out the transformation matrix

        matrix = chart_geometry.compute_matrix_from_page_mm_to_map_surface_coordinates ()

        # This is the center of the map in the page

        map_area_center_x = map_layout.map_to_left_margin_mm + map_layout.map_width_mm / 2.0
        map_area_center_y = map_layout.map_to_top_margin_mm + map_layout.map_height_mm / 2.0

        (pixel_x, pixel_y) = matrix.transform_point (map_area_center_x, map_area_center_y)
        tile_size = provider.get_tile_size ()

        global_pixel_x = chart_geometry.west_tile_idx + pixel_x / tile_size
        global_pixel_y = chart_geometry.north_tile_idx + pixel_y / tile_size

        (lat, lon) = tile_number_to_coordinates (map_layout.zoom, global_pixel_x, global_pixel_y)

        self.assertFloatEquals (lat, map_layout.center_lat)
        self.assertFloatEquals (lon, map_layout.center_lon)

    def test_page_mm_to_lat_lon (self):
        map_layout = self.make_test_map_layout ()
        provider = tile_provider.NullTileProvider ()
        chart_geometry = ChartGeometry (map_layout, provider)

        chart_geometry.compute_extents_of_downloaded_tiles ()

        map_area_center_x = map_layout.map_to_left_margin_mm + map_layout.map_width_mm / 2.0
        map_area_center_y = map_layout.map_to_top_margin_mm + map_layout.map_height_mm / 2.0

        (lat, lon) = chart_geometry.transform_page_mm_to_lat_lon (map_area_center_x, map_area_center_y)

        self.assertFloatEquals (lat, map_layout.center_lat)
        self.assertFloatEquals (lon, map_layout.center_lon)
