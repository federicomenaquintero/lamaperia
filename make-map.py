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

    if args.from_lat == None:
        print ("Missing --from-lat=FLOAT argument")
        valid = False

    if args.from_lon == None:
        print ("Missing --from-lon=FLOAT argument")
        valid = False

    have_to_lon = args.to_lon != None
    have_to_lat = args.to_lat != None

    have_width_tiles  = args.width_tiles != None
    have_height_tiles = args.height_tiles != None

    if not ((have_to_lon and have_to_lat and not have_width_tiles and not have_height_tiles)
            or (not have_to_lon and not have_to_lat and have_width_tiles and have_height_tiles)):
        print (
            """Expecting either:
            --to-lon=FLOAT --to-lat=FLOAT
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

parser = argparse.ArgumentParser (description = "Make a map from Mapbox tiles")

parser.add_argument ("--from-lat", type=float, metavar="FLOAT")
parser.add_argument ("--from-lon", type=float, metavar="FLOAT")
parser.add_argument ("--to-lat", type=float, metavar="FLOAT")
parser.add_argument ("--to-lon", type=float, metavar="FLOAT")
parser.add_argument ("--width-tiles", type=int, metavar="INT")
parser.add_argument ("--height-tiles", type=int, metavar="INT")
parser.add_argument ("--zoom", type=int, metavar="INT", default=15)
parser.add_argument ("--output", type=argparse.FileType("wb"), metavar="FILENAME")

args = parser.parse_args ()

validate_args (args)

(leftmost_tile, topmost_tile) = coordinates_to_tile_number (args.zoom, args.from_lat, args.from_lon)

if args.width_tiles != None and args.height_tiles != None:
    width_tiles = args.width_tiles
    height_tiles = args.height_tiles
elif args.to_lat != None and args.to_lon != None:
    (rightmost_tile, bottommost_tile) = coordinates_to_tile_number (args.zoom, args.to_lat, args.to_lon)
    width_tiles = rightmost_tile - leftmost_tile + 1
    height_tiles = bottommost_tile - topmost_tile + 1

    if width_tiles < 1 or height_tiles < 1:
        print ("Please specify --from-lat/--from-lon and --to-lat/--to-lon so that they are the top left and bottom right of the area to render, respectively")
        sys.exit (1)

have_tile_size = False
tile_size = 0
image_surf = None
cr = None

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

print ("Writing {0}".format (args.output))
image_surf.write_to_png (args.output)
