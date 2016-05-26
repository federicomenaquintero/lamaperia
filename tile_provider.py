import requests
import unittest
import cairo
import io

class TileProvider:
    def get_tile_png (self, z, x, y):
        pass

    def get_tile_size (self):
        pass

class MapboxTileProvider (TileProvider):
    def __init__ (self, access_token, username, style_id):
        self.access_token = access_token
        self.username = username
        self.style_id = style_id

    def get_uri_for_tile (self, z, x, y):
        uri = "https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/{z}/{x}/{y}".format (
            username = self.username,
            style_id = self.style_id,
            z = z,
            x = x,
            y = y)

        uri = "http://127.0.0.1:8080/fmq-mapbox/{z}/{x}/{y}.png".format (z = z, x = x, y = y)

        return uri

    def make_request_for_tile (self, z, x, y):
        url = self.get_uri_for_tile (z, x, y)
#        r = requests.get (url,
#                          params = { 'access_token' : self.access_token })
        r = requests.get (url)
        return r

    def get_tile_png (self, z, x, y):
        r = self.make_request_for_tile (z, x, y)
        return r.content

    def get_tile_size (self):
        return 512

class NullTileProvider (TileProvider):
    def get_tile_png (self, z, x, y):
        f = open ("null-tile-512.png", "rb")
        data = f.read ()
        f.close ()

        return data

    def get_tile_size (self):
        return 512

#################### tests ####################

class TestNullTileProvider (unittest.TestCase):
    def test_null_tile_provider_makes_sense (self):
        tile_provider = NullTileProvider ()

        tile_size = tile_provider.get_tile_size ()

        png_data = tile_provider.get_tile_png (0, 0, 0)
        self.assertIsNotNone (png_data)

        tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))
        self.assertIsNotNone (tile_surf)

        self.assertEqual (tile_surf.get_width (), tile_size)
        self.assertEqual (tile_surf.get_height (), tile_size)
