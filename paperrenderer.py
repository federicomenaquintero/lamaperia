from units import *
import cairo
import chartrenderer

class PaperRenderer:
    def __init__ (self):
        self.paper_width_mm = inch_to_mm (11.0)
        self.paper_height_mm = inch_to_mm (8.5)

    def set_paper_size_mm (self, width_mm, height_mm):
        self.paper_width_mm = width_mm
        self.paper_height_mm = height_mm

    def render (self, format, filename, chart_renderer):
        width_pt = mm_to_pt (self.paper_width_mm)
        height_pt = mm_to_pt (self.paper_height_mm)

        if format == "svg":
            surface = cairo.SVGSurface (filename, width_pt, height_pt)
        elif format == "pdf":
            surface = cairo.PDFSurface (filename, width_pt, height_pt)
        else:
            raise ValueError ("rendering format was specified as '{0}'; it must be one of 'svg', 'pdf'".format (format))

        # These surfaces are created in points, but we want to render everything in millimeters.
        # Set up a scaling transformation and render everything based on that.

        cr = cairo.Context (surface)
        factor = mm_to_pt (1.0)
        cr.scale (factor, factor)

        chart_renderer.render_to_cairo (cr)

        surface.show_page ()
