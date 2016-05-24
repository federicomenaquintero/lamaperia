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
    parser.add_argument ("--format",       type = str, required = True, metavar = "STRING")
    parser.add_argument ("--output",       type = str, required = True, metavar = "FILENAME")

    args = parser.parse_args ()

    json_config = open (args.config).read ()
    map_layout = maplayout.MapLayout ()
    map_layout.parse_json (json_config)

    paper_renderer = paperrenderer.PaperRenderer (map_layout)

    chart_renderer = chartrenderer.ChartRenderer (map_layout)
    chart_renderer.set_map_size_mm (inch_to_mm (10.25), inch_to_mm (7.75))
    chart_renderer.set_map_to_top_left_margin_mm (inch_to_mm (0.375), inch_to_mm (0.375))

    chart_renderer.set_tile_provider (tile_provider.MapboxTileProvider (mapbox_access_params["access_token"],
                                                                        mapbox_access_params["username"],
                                                                        mapbox_access_params["style_id"]))

    paper_renderer.render (args.format, args.output, chart_renderer)

if __name__ == "__main__":
    main ()
