import math

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
