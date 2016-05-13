#!/usr/bin/env python3
#
# python3 make-map.py --lat=yyy --lon=xxx --width-tiles=5 --height-tiles=5 --output=foo.png

import os
import sys
import requests  # http://docs.python-requests.org/en/master/
import argparse
import math
import io
import cairo
import tempfile
import re
import pyproj

mapbox_access_params = {
    'access_token' : 'pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ',
    'username'     : 'federicomenaquintero',
    'style_id'     : 'cil44s8ep000c9jm18x074iwv'
}

def get_mapbox_uri_for_tile (access_params, z, x, y):
    access_token = access_params['access_token']
    username     = access_params['username']
    style_id     = access_params['style_id']

    uri = "https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/{z}/{x}/{y}".format (
        username = username,
        style_id = style_id,
        z = z,
        x = x,
        y = y)

    return uri

def get_tile_png (access_params, z, x, y):
    url = get_mapbox_uri_for_tile (access_params, z, x, y)

    r = requests.get (url,
                      params = { 'access_token' : access_params['access_token'] })

    return r.content

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

def find_tile_size_from_png_data (png_data):
    # total hack

    # f = tempfile.TemporaryFile ()
    # f.write (png_data)

    surface = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))
    return surface.get_width ()

def validate_args (args):
    valid = True

    if args.from_lat == None:
        print ("Missing --from-lat=DEGREES argument")
        valid = False

    if args.from_lon == None:
        print ("Missing --from-lon=DEGREES argument")
        valid = False

    have_to_lon = args.to_lon != None
    have_to_lat = args.to_lat != None

    have_width_tiles  = args.width_tiles != None
    have_height_tiles = args.height_tiles != None

    if not ((have_to_lon and have_to_lat and not have_width_tiles and not have_height_tiles)
            or (not have_to_lon and not have_to_lat and have_width_tiles and have_height_tiles)):
        print (
"""Expecting either:
  --to-lon=DEGREES --to-lat=DEGREES
or:
  --width-tiles=N --height-tiles=N""")
        valid = False

    if have_width_tiles and args.width_tiles < 1:
        print ("--width-tiles expects an integer greater than zero")
        valid = False

    if have_height_tiles and args.height_tiles < 1:
        print ("--height-tiles expects an integer greater than zero")
        valid = False

    if args.zoom == None:
        print ("Missing --zoom=N argument")
        valid = False
    elif args.zoom < 0 or args.zoom > 20:
        print ("--zoom-tiles expects an integer in the [0, 20] range")
        valid = False

    if args.output == None:
        print ("Missing --output=FILENAME argument")
        valid = False

    if not valid:
        sys.exit (1)

####################################################################

def main ():
    parser = argparse.ArgumentParser (description = "Makes a PNG map from Mapbox tiles.",
                                      epilog =
"""DEGREES can be given as decimal degrees (e.g. "19.5" or "-19.5")
or as degrees/minutes as "19d30m"
or as degrees/minutes/seconds as "19d30m5s".
Degrees can be negative as in "-19d30m".
The default zoom value is 15.
""")

    parser.add_argument ("--from-lat",     type = str, required = True, metavar = "DEGREES")
    parser.add_argument ("--from-lon",     type = str, required = True, metavar="DEGREES")
    parser.add_argument ("--to-lat",       type = str, metavar = "DEGREES")
    parser.add_argument ("--to-lon",       type = str, metavar = "DEGREES")
    parser.add_argument ("--width-tiles",  type = int, metavar = "INT")
    parser.add_argument ("--height-tiles", type = int, metavar = "INT")
    parser.add_argument ("--zoom",         type = int, metavar = "INT", default = 15)
    parser.add_argument ("--output",       type = argparse.FileType("wb"), metavar = "FILENAME")

    args = parser.parse_args ()

    validate_args (args)

    from_lat = parse_degrees (args.from_lat)
    from_lon = parse_degrees (args.from_lon)

    (leftmost_tile, topmost_tile) = coordinates_to_tile_number (args.zoom, from_lat, from_lon)

    if args.width_tiles != None and args.height_tiles != None:
        width_tiles = args.width_tiles
        height_tiles = args.height_tiles
    elif args.to_lat != None and args.to_lon != None:
        to_lat = parse_degrees (args.to_lat)
        to_lon = parse_degrees (args.to_lon)

        (rightmost_tile, bottommost_tile) = coordinates_to_tile_number (args.zoom, to_lat, to_lon)
        width_tiles = rightmost_tile - leftmost_tile + 1
        height_tiles = bottommost_tile - topmost_tile + 1

        if width_tiles < 1 or height_tiles < 1:
            print ("Please specify --from-lat/--from-lon and --to-lat/--to-lon so that they are the top left and bottom right of the area to render, respectively")
            print ("from_lat={0}, from_lon={1}".format (from_lat, from_lon))
            print ("to_lat={0}, to_lon={1}".format (to_lat, to_lon))
            print ("leftmost_tile={0} topmost_tile={1}".format (leftmost_tile, topmost_tile))
            print ("rightmost_tile={0} bottommost_tile={1}".format (rightmost_tile, bottommost_tile))
            sys.exit (1)

    have_tile_size = False
    tile_size = 0
    image_surf = None
    cr = None

    (lat1, lon1) = tile_number_to_coordinates (args.zoom, leftmost_tile, topmost_tile)
    (lat2, lon2) = tile_number_to_coordinates (args.zoom, leftmost_tile + width_tiles, topmost_tile + height_tiles)

    p = pyproj.Proj (proj="utm", zone=14, ellps='WGS84') # FIXME: hardcoded zone

    (utm1_e, utm1_n) = p (lon1, lat1)
    (utm2_e, utm2_n) = p (lon2, lat1)
    (utm3_e, utm3_n) = p (lon1, lat2)
    (utm4_e, utm4_n) = p (lon2, lat2)
    
    print ("Coordinates at corners: ({0}, {1}), ({2}, {3})".format (lat1, lon1, lat2, lon2))
    print ("UTM at corners: ({0}, {1}), ({2}, {3})".format (utm1_e, utm1_n, utm2_e, utm2_n))
    print ("                ({0}, {1}), ({2}, {3})".format (utm3_e, utm3_n, utm4_e, utm4_n))

    print ("Downloading {0} tiles ({1} * {2}) at zoom={3}...".format (width_tiles * height_tiles, width_tiles, height_tiles, args.zoom))

    tiles_downloaded = 0

    for y in range (0, height_tiles):
        for x in range (0, width_tiles):
            tile_x = x + leftmost_tile
            tile_y = y + topmost_tile

            tiles_downloaded += 1
            print ("Downloading tile {0}".format(tiles_downloaded), end='\r', flush=True)

            png_data = get_tile_png (mapbox_access_params, args.zoom, tile_x, tile_y)

            if not have_tile_size:
                have_tile_size = True
                tile_size = find_tile_size_from_png_data (png_data)

                print ("Final image will be {0} * {1} pixels in size".format (tile_size * width_tiles, tile_size * height_tiles))

                image_surf = cairo.ImageSurface (cairo.FORMAT_RGB24, tile_size * width_tiles, tile_size * height_tiles)
                cr = cairo.Context (image_surf)

            tile_xpos = x * tile_size
            tile_ypos = y * tile_size

            tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))

            cr.set_source_surface (tile_surf, tile_xpos, tile_ypos)
            cr.paint ()

    print ("")

    min_utm_e = int (min (utm1_e, utm2_e, utm3_e, utm4_e))
    max_utm_e = int (max (utm1_e, utm2_e, utm3_e, utm4_e)) + 1

    min_utm_n = int (min (utm1_n, utm2_n utm3_n, utm4_n))
    max_utm_n = int (max (utm1_n, utm2_n utm3_n, utm4_n)) + 1

    p = pyproj.Proj (proj="utm", zone=14, ellps='WGS84', inverse=True) # FIXME: hardcoded zone

    # make rectangular array of converted coordinates

    for n in range (min_utm_n, max_utm_n):
        for e in range (min_utm_e, max_utm_e):
            # convert UTM coordinates to geographic
            # convert geographic to pixels
            #

    print ("Writing {0}".format (args.output))
    image_surf.write_to_png (args.output)

if __name__ == "__main__":
    main ()
