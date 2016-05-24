#!/usr/bin/env python3
#
# python3 make-map.py --lat=yyy --lon=xxx --width-tiles=5 --height-tiles=5 --output=foo.png

import os
import sys
import paperrenderer
import chartrenderer
import tile_provider
import argparse
import math
import cairo
from units import *
from parsedegrees import *
import maplayout

mapbox_access_params = {
    'access_token' : 'pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ',
    'username'     : 'federicomenaquintero',
    'style_id'     : 'cil44s8ep000c9jm18x074iwv'
}

def validate_args (args):
    valid = True

    if args.zoom == None:
        print ("Missing --zoom=N argument")
        valid = False
    elif args.zoom < 0 or args.zoom > 20:
        print ("--zoom-tiles expects an integer in the [0, 20] range")
        valid = False

    if not valid:
        sys.exit (1)

####################################################################

def main ():
    parser = argparse.ArgumentParser (description = "Makes a PDF or SVG map from Mapbox tiles.",
                                      epilog =
"""DEGREES can be given as decimal degrees (e.g. "19.5" or "-19.5")
or as degrees/minutes as "19d30m"
or as degrees/minutes/seconds as "19d30m5s".
Degrees can be negative as in "-19d30m".
The default zoom value is 15.
""")

    parser.add_argument ("--config",       type = str, required = True, metavar = "JSON-FILENAME")
    parser.add_argument ("--center-lat",   type = str, required = True, metavar = "DEGREES")
    parser.add_argument ("--center-lon",   type = str, required = True, metavar = "DEGREES")
    parser.add_argument ("--map-scale",    type = float, default = 50000.0, metavar = "FLOAT")
    parser.add_argument ("--zoom",         type = int, metavar = "INT", default = 15)
    parser.add_argument ("--format",       type = str, required = True, metavar = "STRING")
    parser.add_argument ("--output",       type = str, required = True, metavar = "FILENAME")

    args = parser.parse_args ()

    validate_args (args)

    json_config = open (args.config).read ()
    map_layout = maplayout.MapLayout ()
    map_layout.parse_json (json_config)

    center_lat = parse_degrees (args.center_lat)
    center_lon = parse_degrees (args.center_lon)

    paper_renderer = paperrenderer.PaperRenderer ()
    paper_renderer.set_paper_size_mm (map_layout.paper_width_mm, map_layout.paper_height_mm)

    chart_renderer = chartrenderer.ChartRenderer ()
    chart_renderer.set_map_size_mm (inch_to_mm (10.25), inch_to_mm (7.75))
    chart_renderer.set_map_to_top_left_margin_mm (inch_to_mm (0.375), inch_to_mm (0.375))
    chart_renderer.set_zoom (args.zoom)
    chart_renderer.set_map_center_and_scale (center_lat, center_lon, args.map_scale)

    chart_renderer.set_tile_provider (tile_provider.MapboxTileProvider (mapbox_access_params["access_token"],
                                                                        mapbox_access_params["username"],
                                                                        mapbox_access_params["style_id"]))

    paper_renderer.render (args.format, args.output, chart_renderer)

if __name__ == "__main__":
    main ()
