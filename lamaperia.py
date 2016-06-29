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
from wizard import config_wizard

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

def main (config_data):
    parser = argparse.ArgumentParser (description = "Makes a PDF or SVG map from Mapbox tiles.")

    parser.add_argument ("--config", type = jsonfile, required = True, metavar = "JSON-FILENAME")
    parser.add_argument ("--format", type = str,      required = True, metavar = "STRING")
    parser.add_argument ("--output", type = str,      required = True, metavar = "FILENAME")

    args = parser.parse_args ()

    json_config = args.config
    map_layout = maplayout.MapLayout ()
    map_layout.load_from_json (json_config)

    provider_classname = '{}TileProvider'.format (config_data['provider'].capitalize())
    provider_class = getattr(tile_provider, provider_classname)
    provider = provider_class(config_data)

    geometry = chartgeometry.ChartGeometry (map_layout, provider)

    paper_renderer = paperrenderer.PaperRenderer (map_layout)
    chart_renderer = chartrenderer.ChartRenderer (geometry)

    geometry.compute_extents_of_downloaded_tiles ()

    (lat1, lon1) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm, map_layout.map_to_top_margin_mm + map_layout.map_height_mm)
    (lat2, lon2) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm + map_layout.map_width_mm, map_layout.map_to_top_margin_mm)

    print ("Map bounds: {0} {1} {2} {3}".format (lat1, lon1, lat2, lon2))

    paper_renderer.render (args.format, args.output, chart_renderer)

if __name__ == "__main__":
    data_file = os.path.join (os.path.expanduser ("~"), '.mkmaprc')
    try:
        mkmaprc = open (data_file)
    except IOError as e:
        print("You don't have a config yet.")
        answ = input("Create one? [Y/n] ").lower ()
        if answ.startswith('y') or not answ:
            config_data = config_wizard ()
        else:
            print("I really need a config file...")
            exit(0)
    else:
        config_data = json.load (open (data_file))

    main (config_data)
