import cairo
import units
from gi.repository import Pango
from gi.repository import PangoCairo

def set_source_rgb(cr, color):
    cr.set_source_rgb (color[0], color[1], color[2])

def rectangle_thickness_outside (cr, x, y, width, height, thickness):
    cr.set_line_join (cairo.LINE_JOIN_MITER)
    cr.set_line_width (thickness)
    cr.rectangle (x - thickness / 2.0,
                  y - thickness / 2.0,
                  width + thickness,
                  height + thickness)
    cr.stroke ()

def rectangle_thickness_inside (cr, x, y, width, height, thickness):
    cr.set_line_join (cairo.LINE_JOIN_MITER)
    cr.set_line_width (thickness)
    cr.rectangle (x + thickness / 2.0,
                  y + thickness / 2.0,
                  width - thickness,
                  height - thickness)
    cr.stroke ()

# anchor can be nw, n, ne, w, c, e, sw, s, se, baseline_w, baseline_c, baseline_e
def render_text (cr, x, y, anchor, font_description, str):
    layout = PangoCairo.create_layout (cr)
    layout.set_font_description (font_description)
    layout.set_text (str, -1)

    cr.save ()

    cr.move_to (x, y)

    # this is a quirk.  This function assumes that the CTM is set to millimeters, and Pango really wants points.
    cr.scale (pt_to_mm (1), pt_to_mm (1))

    (ink_rect, logical_rect) = layout.get_pixel_extents ()
    (xpos, ypos) = cr.get_current_point ()

    if anchor == "nw":
        x_anchor = 0
        y_anchor = 0
    elif anchor == "n":
        x_anchor = 0.5
        y_anchor = 0
    elif anchor == "ne":
        x_anchor = 1
        y_anchor = 0
    elif anchor == "w":
        x_anchor = 0
        y_anchor = 0.5
    elif anchor == "c":
        x_anchor = 0.5
        y_anchor = 0.5
    elif anchor == "e":
        x_anchor = 1
        y_anchor = 0.5
    elif anchor == "sw":
        x_anchor = 0
        y_anchor = 1
    elif anchor == "s":
        x_anchor = 0.5
        y_anchor = 1
    elif anchor == "se":
        x_anchor = 1
        y_anchor = 1
    else:
        baseline = layout.get_baseline () / Pango.SCALE
        y_anchor = baseline / logical_rect.height

        if anchor == "baseline_w":
            x_anchor = 0
        elif anchor == "baseline_c":
            x_anchor = 0.5
        elif anchor == "baseline_e":
            x_anchor = 1
        else:
            raise Exception ("invalid anchor")

    xpos -= x_anchor * logical_rect.width
    ypos -= y_anchor * logical_rect.height

    cr.move_to (xpos, ypos)
    PangoCairo.show_layout (cr.layout)

    cr.restore ()
