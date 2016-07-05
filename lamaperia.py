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
import config
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

    provider_classname = '{}TileProvider'.format (config_data['provider'])
    provider_class = getattr (tile_provider, provider_classname)
    provider = provider_class (config_data)

    geometry = chartgeometry.ChartGeometry (map_layout, provider)

    paper_renderer = paperrenderer.PaperRenderer (map_layout)
    chart_renderer = chartrenderer.ChartRenderer (geometry)

    geometry.compute_extents_of_downloaded_tiles ()

    (lat1, lon1) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm, map_layout.map_to_top_margin_mm + map_layout.map_height_mm)
    (lat2, lon2) = geometry.transform_page_mm_to_lat_lon (map_layout.map_to_left_margin_mm + map_layout.map_width_mm, map_layout.map_to_top_margin_mm)

    print ("Map bounds: {0} {1} {2} {3}".format (lat1, lon1, lat2, lon2))

    paper_renderer.render (args.format, args.output, chart_renderer)

if __name__ == "__main__":
    try:
        config_data = config.config_load ()
    except IOError as e:
        print ("La Mapería is not configured yet.")
        answ = input ("Would you like to configure La Mapería right now? [Y/n] ").lower ()
        if answ.startswith ('y') or not answ:
            config_data = config_wizard ()
        else:
            print ("I'm not smart enough to work without a configuration.  Exiting...")
            exit (1)
    except ValueError as e:
        print ("The configuration in {} is not valid: {}".format (config.config_get_configuration_filename (),
                                                                  e.args[0]))
        exit (1)

    main (config_data)
