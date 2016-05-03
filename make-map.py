#!/usr/bin/env python3

import os
import sys
import requests  # http://docs.python-requests.org/en/master/

opensuse_ca = "/etc/ssl/ca-bundle.pem"

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
                      verify = opensuse_ca,
                      params = { 'access_token' : access_params['access_token'] })

    return r.content

# stolen from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#
# returns (x, y) pair
def coordinates_to_tile_number (z, lat, lon):
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = int ((lon + 180.0) / 360.0 * n)
    ytile = int ((1.0 - math.log (math.tan (lat) + (1 / math.cos (lat))) / math.pi) / 2.0 * n)
    return (xtile, ytile)
