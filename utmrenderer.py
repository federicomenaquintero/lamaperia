import chartgeometry
import pyproj
import math

def longitude_to_zone (lon):
    zone = int (math.round (lon / 6.0 + 30.5))
    return ((zone - 1) % 60) + 1

class UTMRenderer:
    def __init__ (self, chart_geometry):
        assert chart_geometry is not None

        self.geometry = chart_geometry

    def compute_utm_box (self):
        layout = self.geometry.map_layout

        (x1, y1) = (layout.map_to_left_margin_mm,
                    layout.map_to_top_margin_mm)

        (x2, y2) = (layout.map_to_left_margin_mm + layout.map_width_mm,
                    layout.map_to_top_margin_mm + layout.map_height_mm)

        (top_left_lat, top_left_lon) = self.geometry.transform_page_mm_to_lat_lon (x1, y1)
        (top_right_lat, top_right_lon) = self.geometry.transform_page_mm_to_lat_lon (x2, y1)

        (bottom_left_lat, bottom_left_lon) = self.geometry.transform_page_mm_to_lat_lon (x1, y2)
        (bottom_right_lat, bottom_right_lon) = self.geometry.transform_page_mm_to_lat_lon (x2, y2)

        top_left_zone = longitude_to_zone (top_left_lon)
        top_right_zone = longitude_to_zone (top_right_lon)
        bottom_left_zone = longitude_to_zone (bottom_left_lon)
        bottom_right_zone = longitude_to_zone (bottom_right_lon)

        if not (top_left_zone == top_right_zone
                and top_left_zone == bottom_left_zone
                and top_left_zone == bottom_right_zone):
            raise Exception ("All four corners of the map must be in the same UTM zone.  Sorry; this program is dumb.")

        
