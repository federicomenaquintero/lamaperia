import cairo

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
