import requests
import unittest
import cairo
import io

class TileProvider:
    def __init__ (self, config):
        self.config = config

    def get_tile_png (self, z, x, y):
        pass

    def get_tile_size (self):
        pass

class MapboxTileProvider (TileProvider):
    def get_uri_for_tile (self, z, x, y):
        uri = "https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/{z}/{x}/{y}".format (
            username = self.config['mapbox_username'],
            style_id = self.config['mapbox_style_id'],
            z = z,
            x = x,
            y = y)

        return uri

    def get_request_params (self):
        return {
            'access_token' : self.config['mapbox_access_token']
        }

    def make_request_for_tile (self, z, x, y):
        retries = 5

        while retries > 0:
            url = self.get_uri_for_tile (z, x, y)
            r = requests.get (url, params = self.get_request_params ())
            if r.status_code != 200:
                print ("request for {0} returned {1}, retrying...".format (url, r.status_code))
                retries -= 1
                continue
            else:
                break

        if retries == 0:
            r.raise_for_status ()

        return r

    def get_tile_png (self, z, x, y):
        r = self.make_request_for_tile (z, x, y)
        return r.content

    def get_tile_size (self):
        return 512

class TilestacheTileProvider (MapboxTileProvider):

    def get_uri_for_tile (self, z, x, y):
        uri = "http://{host}:{port}/fmq-mapbox/{z}/{x}/{y}.png".format (
            host = self.config['tilestache_host'],
            port = self.config['tilestache_port'],
            z = z,
            x = x,
            y = y)

        return uri

    def get_request_params (self):
        return {}

class NullTileProvider (TileProvider):
    def __init__ (self):
        self.north_tile_requested_limit = -1
        self.south_tile_requested_limit = -1
        self.east_tile_requested_limit = -1
        self.west_tile_requested_limit = -1

    def get_tile_png (self, z, x, y):
        assert z >= 0
        assert x >= 0
        assert y >= 0

        f = open ("null-tile-512.png", "rb")
        data = f.read ()
        f.close ()

        if self.west_tile_requested_limit < 0:
            self.west_tile_requested_limit = x
        elif x < self.west_tile_requested_limit:
            self.west_tile_requested_limit = x

        if self.east_tile_requested_limit < 0:
            self.east_tile_requested_limit = x
        elif x > self.east_tile_requested_limit:
            self.east_tile_requested_limit = x

        if self.north_tile_requested_limit < 0:
            self.north_tile_requested_limit = y
        elif y < self.north_tile_requested_limit:
            self.north_tile_requested_limit = y

        if self.south_tile_requested_limit < 0:
            self.south_tile_requested_limit = y
        elif y > self.south_tile_requested_limit:
            self.south_tile_requested_limit = y

        return data

    def get_tile_size (self):
        return 512

#################### tests ####################

class TestNullTileProvider (unittest.TestCase):
    def test_null_tile_provider_has_initialized_request_limits (self):
        tile_provider = NullTileProvider ()
        self.assertEqual (tile_provider.north_tile_requested_limit, -1)
        self.assertEqual (tile_provider.south_tile_requested_limit, -1)
        self.assertEqual (tile_provider.east_tile_requested_limit, -1)
        self.assertEqual (tile_provider.west_tile_requested_limit, -1)

    def test_null_tile_provider_makes_sense (self):
        tile_provider = NullTileProvider ()

        tile_size = tile_provider.get_tile_size ()

        png_data = tile_provider.get_tile_png (0, 0, 0)
        self.assertIsNotNone (png_data)

        tile_surf = cairo.ImageSurface.create_from_png (io.BytesIO (png_data))
        self.assertIsNotNone (tile_surf)

        self.assertEqual (tile_surf.get_width (), tile_size)
        self.assertEqual (tile_surf.get_height (), tile_size)

    def test_null_tile_provider_maintains_requested_limits (self):
        tile_provider = NullTileProvider ()

        tile_provider.get_tile_png (15, 20, 30)
        tile_provider.get_tile_png (15, 40, 50)

        self.assertEqual (tile_provider.north_tile_requested_limit, 30)
        self.assertEqual (tile_provider.south_tile_requested_limit, 50)
        self.assertEqual (tile_provider.west_tile_requested_limit, 20)
        self.assertEqual (tile_provider.east_tile_requested_limit, 40)
