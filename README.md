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
called `mymap.json`:

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
    "center-lat" : "19.34166666",
    "center-lon" : "-96.5",
```

Decimal degrees can also be specified as floats rather than strings,
so you can use `-96.5` instead of `"-96.5"` in the example above.
Sexagesimal degrees must always be specified as strings.

### Choosing a Paper Size

La Mapería lets you specify units in millimeters or in inches.  A
value in mm is specified as a string like `"25 mm"`; a value in inches
as `"10 in"`.

You can specify the paper size with two parameters in the
configuration file, `paper-width` and `paper-height`.  For example,
this describes an A4 sheet of paper in landscape format:

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

### Map scale and Zoom

By default La Mapería creates maps at 1:50,000 scale.  For this kind
of scale, OpenStreetMap has a comfortable level of detail at zoom=15.

```json
    "map-scale" : 50000,

    "zoom" : 15,
```

The `map-scale` parameter is the denominator of the scale you want.
To have a scale of 1:25,000, use `"map-scale" : 25000`.

You may want to experiment with the `zoom` level depending on the map
scale you want, the amount of detail that OpenStreetMap has for your
map's area, and the actual rendering style for your tiles.

### The Map Scale Indicator

La Mapería can render a popular style of map scale indicator.  By
default it shows 1 Km subdivided in 100 m increments (the "small
divisions"), followed by 4 Km subdivided in 1 Km increments (the
"large divisions").  

Just for illustrative purposes, here are eight few small divisions on
the left, and two small divisions on the right:

```
+---|---|---|---|---|---|---|---|---|-----------------------------------|-----------------------------------|
|###|   |###|   |###|   |###|   |###|                                   |###################################|
+---|---|---|---|---|---|---|---|---|-----------------------------------|-----------------------------------|
```

So, to have 10 small divisions of 100 meters each, plus 4 large
divisions of 1 Km each, you would use this:

```
    "scale-small-divisions-interval-m" : 100,
    "scale-num-small-divisions" : 10,

    "scale-large-divisions-interval-m" : 1000,
    "scale-num-large-divisions" : 4,

```

In addition, the divisions get labels so that you can see what they
refer to, but not all divisions get a label to avoid visual clutter.
You can specify where to place the ticks and labels, and the actual
label strings, with separate `scale-small-ticks-m` and
`scale-large-ticks-m` parameters.  

Let's look at an example of `scale-large-ticks-m` for the
large-divisions section of the scale:

```
    "scale-large-ticks-m" : [ 0,    "0",
                              1000, "1",
                              2000, "2",
                              3000, "3",
                              4000, "4 Km" ],
```

This means that at zero meters, there will be a label of "0".  At 1000
meters, there will be a label of "1".  And so on, until at 4000 meters
there will be a label that says "4 Km".  Usually showing the units
only once for each of the small-divisions or large-divisions sections
of the scale indicator is enough.  If you specified "0 Km", "1 Km", "2
Km", etc., the scale would look a lot more cluttered.

Now, let's look at an example of `scale-small-ticks-m` for the
small-divisions section of the scale, together with the parameters for
that section's divisions:

```
    "scale-small-divisions-interval-m" : 100,
    "scale-num-small-divisions" : 4,

    "scale-small-ticks-m" : [ 0, "0 m",
                              200, "200",
                              400, "400" ],
```

At zero meters, there will be a label of "0 m".  At 200 meters, a
label of "200", and at 400 meters, a label of "400".  So, while the
scale has 4 small-divisions at every 100 meters, they are only
labeled at every 200 meters, to avoid clutter.
