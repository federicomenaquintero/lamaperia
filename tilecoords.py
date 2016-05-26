import math
import testutils

# stolen from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#
# returns (x, y) pair

def coordinates_to_tile_and_fraction (z, lat, lon):
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - math.log (math.tan (lat_rad) + (1 / math.cos (lat_rad))) / math.pi) / 2.0 * n
    return (xtile, ytile)

def coordinates_to_tile_number (z, lat, lon):
    (xtile, ytile) = coordinates_to_tile_and_fraction (z, lat, lon)
    return (int (xtile), int (ytile))

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

#################### tests ####################

class TestTileCoords (testutils.TestCaseHelper):
    def test_tile_number_and_fraction_roundtrips_to_coordinates (self):
        start_lat = 19.4621106
        start_lon = -96.9040473

        for zoom in range (0, 20):
            (tile_x, tile_y) = coordinates_to_tile_and_fraction (zoom, start_lat, start_lon)
            (end_lat, end_lon) = tile_number_to_coordinates (zoom, tile_x, tile_y)

            self.assertFloatEquals (start_lat, end_lat)
            self.assertFloatEquals (start_lon, end_lon)

    def test_cerro_malinche_is_in_the_correct_tile (self):
        lat = 19.4621106
        lon = -96.9040473
        zoom = 15

        expected_tile_x = 7563
        expected_tile_y = 14577

        (tile_x, tile_y) = coordinates_to_tile_number (zoom, lat, lon)

        self.assertFloatEquals (tile_x, expected_tile_x)
        self.assertFloatEquals (tile_y, expected_tile_y)
