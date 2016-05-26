import math

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
