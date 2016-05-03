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

# stolen from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#
# returns (x, y) pair
def coordinates_to_tile_number (z, lat, lon):
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = int ((lon + 180.0) / 360.0 * n)
    ytile = int ((1.0 - math.log (math.tan (lat_rad) + (1 / math.cos (lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def find_tile_size_from_png_data (png_data):
    # total hack

    # f = tempfile.TemporaryFile ()
    # f.write (png_data)

    surface = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))
    return surface.get_width ()

def validate_args (args):
    valid = True

    if args.lat == None:
        print ("Missing --lat=FLOAT argument")
        valid = False

    if args.lon == None:
        print ("Missing --lon=FLOAT argument")
        valid = False

    if args.width_tiles == None:
        print ("Missing --width-tiles=N argument")
        valid = False
    elif args.width_tiles < 1:
        print ("--width-tiles expects an integer greater than zero")
        valid = False

    if args.zoom == None:
        print ("Missing --zoom=N argument")
        valid = False
    elif args.zoom < 0 or args.zoom > 20:
        print ("--zoom-tiles expects an integer in the [0, 20] range")
        valid = False

    if args.height_tiles == None:
        print ("Missing --height-tiles=N argument")
        valid = False
    elif args.width_tiles < 1:
        print ("--height-tiles expects an integer greater than zero")
        valid = False

    if args.output == None:
        print ("Missing --output=FILENAME argument")
        valid = False

    if not valid:
        sys.exit (1)

####################################################################

parser = argparse.ArgumentParser (description = "Make a map from Mapbox tiles",
                                  formatter_class = argparse.MetavarTypeHelpFormatter)

parser.add_argument ("--lat", type=float)
parser.add_argument ("--lon", type=float)
parser.add_argument ("--zoom", type=int)
parser.add_argument ("--width-tiles", type=int)
parser.add_argument ("--height-tiles", type=int)
parser.add_argument ("--output", type=argparse.FileType("wb"))

args = parser.parse_args ()

validate_args (args)

(leftmost_tile, topmost_tile) = coordinates_to_tile_number (args.zoom, args.lat, args.lon)

have_tile_size = False
tile_size = 0
image_surf = None
cr = None

for y in range (0, args.height_tiles):
    for x in range (0, args.width_tiles):
        tile_x = x + leftmost_tile
        tile_y = y + topmost_tile

        print ("Downloading z={0}, x={1}, y={2}".format (args.zoom, x, y))
        png_data = get_tile_png (mapbox_access_params, args.zoom, tile_x, tile_y)

        if not have_tile_size:
            have_tile_size = True
            tile_size = find_tile_size_from_png_data (png_data)
            image_surf = cairo.ImageSurface (cairo.FORMAT_RGB24, tile_size * args.width_tiles, tile_size * args.height_tiles)
            cr = cairo.Context (image_surf)

        tile_xpos = x * tile_size
        tile_ypos = y * tile_size

        tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))

        cr.set_source_surface (tile_surf, tile_xpos, tile_ypos)
        cr.paint ()

print ("Writing {0}".format (args.output))
image_surf.write_to_png (args.output)
