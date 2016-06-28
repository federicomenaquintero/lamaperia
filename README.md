La Mapería
==========

La Mapería ("the map store") lets you create maps suitable for
printing, from OpenStreetMap raster tiles.  While in theory it works
with any provider of such tiles, in practice it is best to use it with
a map style that is actually designed to be printed, instead of just
viewed on a screen.

How It Works
------------

La Mapería downloads tiles for a particular region, and scales and
places them onto a page.  It draws a frame around the map's contents,
with arc-minute markings, and also draws a map scale so you know what
distance on the map corresponds to the equivalent distance in the real
world.

La Mapería works best for maps at scales 1:100,000 and larger ("more
zoom").  The amount of detail in the resulting maps depends on the
OpenStreetMap zoom level that you choose, and of course, on the actual
style for rendering that your tile provider uses.

Quick Start
-----------

To create a map, you need to create a little configuration file that
specifies how the map will look and which region it will show.  These
configuration files are in JSON format.

### For the impatient

Here is a minimal configuration that will give you a map at 1:50,000
scale for printing in US-letter paper.  That's the default paper size;
later we will see how to change it.  Put the following in a file
called mymap.json:

```json
{
    "center-lat" : "19d28m43s",
    "center-lon" : "-96d53m29s",
    "map-scale"  : 50000
}
```

Now, run this:

```
python3 lamaperia.py --config mymap.json --format pdf --output mymap.pdf
```

If everything works well, you'll get a mymap.pdf with the area where I
like to ride my bike.

Now you are ready to look at the `examples/` directory.  Most of the
files there look the same, and they just change the paper size and the
region to show in the map.

### Choosing the Region to Show

The region that gets shown in the map is determined by the
geographical coordinates (latitude, longitude) at the center of the
map.  You can specify them with the `center-lat` and `center-lon`
options in the configuration file.  Both can be specified as strings,
in either sexagesimal degrees (degrees, minutes, seconds) or decimal
degrees.  For example, the following coordinate pairs describe the
same point (latitude = 19°20'30", longitude = -96°30').

```json
    # sexagesimal
    "center-lat" : "19d20m30s",
    "center-lon" : "-96d30m",

    # decimal
    "center-lat" : "19.3333333",
    "center-lon" : "-96.5",
```

Decimal degrees can also be specified as floats rather than strings,
so you can use `-96.5` instead of `"-96.5"` in the example above.
Sexagesimal degrees must always be specified as strings.

### Choosing a Paper Size

La Mapería lets you specify units in millimeters or in inches.  A
value in mm is specified as a string, for example `"25 mm"` or `"10
in"`.

You can specify the paper size with two parameters in the
configuration file, `paper-width` and `paper-height`.  For example,
this describes an A4 sheet of paper:

```json
    "paper-width"  : "297 mm",
    "paper-height" : "210 mm",
```

and the following describes a US Ledger sheet of paper:

```json
   "paper-width"  : "17 in",
   "paper-height" : "11 in",
```

### Positioning the map and scale

The map is a rectangle in the sheet of paper, and La Mapería wants to
know its upper-left corner plus its width and height.  Also, it wants
to know where to place the map scale - the visual scale that tells you
how big a kilometer is on the map.

Here we create a 60 cm square sheet of paper, and give it a map that
is 56 cm wide and 55 cm tall.  This leaves us enough room for the map
scale below the map itself.

```
{
    "paper-width"  : "600 mm",
    "paper-height" : "600 mm",

    "map-width"  : "560 mm",
    "map-height" : "550 mm",
    "map-to-left-margin" : "20 mm",
    "map-to-top-margin" : "20 mm",

    "scale-xpos" : "300 mm",
    "scale-ypos" : "580 mm"
}
```

The `paper-width` and `paper-height` parameters are as described
above; they define the paper size.

The `map-width` and `map-height` parameters describe the size of the
map area.  This does not include the frame around the map nor the
arc-minutes labels; those go outside the frame area.  This is why you
must leave some margin around the map itself.

The map area gets placed in the page with the `map-to-left-margin` and
`map-to-top-margin` parameters; they are the upper-left corner of the
map area.  Make sure your printer can accomodate these margins, and
that the map's frame and arc-minutes labels actually fit in them.

Finally, the `scale-xpos` and `scale-ypos` parameters specify the
position of the top-center of the map scale.

### Deciding What to Show

The following parameters are booleans; you can specify `true` or
`false` for them.  They all default to `true`.

`draw-map-frame` - Whether to draw a frame around the map.  If you
want a "naked" map, set this to false.

`draw-ticks` - Whether to draw arc-minute ticks around the map frame;
this only works if `draw-map-frame` is true.

`draw-scale` - Whether to draw the map scale.  Maybe La Mapería's
output is not your final map, and you intend to show the scale in
another way.

