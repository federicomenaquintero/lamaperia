import requests

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
