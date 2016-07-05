#!/usr/bin/env python3

import os
import sys
import paperrenderer
import chartrenderer
import tile_provider
import argparse
import math
import cairo
import json
from units import *
from parsedegrees import *
import maplayout
import chartgeometry

mapbox_access_params = {
    'access_token' : 'pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ',
    'username'     : 'federicomenaquintero',
    'style_id'     : 'cil44s8ep000c9jm18x074iwv'
}

####################################################################

def jsonfile (filename):
    try:
        file = open (filename)
    except IOError as e:
        raise argparse.ArgumentTypeError ("can't open '{0}': {1}".format (filename, e))

    try:
        data = json.load (open (filename))
    except ValueError as e:
        msg = "file {0} is not valid JSON: {1}".format (filename, e.args[0])
        raise argparse.ArgumentTypeError (msg)

    return data

def main ():
    parser = argparse.ArgumentParser (description = "Makes a PDF or SVG map from Mapbox tiles.")

    parser.add_argument ("--config", type = jsonfile, required = True, metavar = "JSON-FILENAME")
    parser.add_argument ("--format", type = str,      required = True, metavar = "STRING")
    parser.add_argument ("--output", type = str,      required = True, metavar = "FILENAME")

    args = parser.parse_args ()

    json_config = args.config
    map_layout = maplayout.MapLayout ()
    map_layout.load_from_json (json_config)

    provider = tile_provider.MapboxTileProvider (mapbox_access_params["access_token"],
                                                 mapbox_access_params["username"],
                                                 mapbox_access_params["style_id"])

    geometry = chartgeometry.ChartGeometry (map_layout, provider)

    paper_renderer = paperrenderer.PaperRenderer (map_layout)
    chart_renderer = chartrenderer.ChartRenderer (geometry)

    geometry.compute_extents_of_downloaded_tiles ()

    (lat1, lon1) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm, map_layout.map_to_top_margin_mm + map_layout.map_height_mm)
    (lat2, lon2) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm + map_layout.map_width_mm, map_layout.map_to_top_margin_mm)

    print ("Map bounds: {0} {1} {2} {3}".format (lat1, lon1, lat2, lon2))

    paper_renderer.render (args.format, args.output, chart_renderer)

if __name__ == "__main__":
    main ()
