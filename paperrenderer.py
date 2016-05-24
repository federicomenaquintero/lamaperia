from units import *
import cairo
import chartrenderer

class PaperRenderer:
    def __init__ (self, layout):
        self.layout = layout

    def render (self, format, filename, chart_renderer):
        width_pt = mm_to_pt (self.layout.paper_width_mm)
        height_pt = mm_to_pt (self.layout.paper_height_mm)

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
