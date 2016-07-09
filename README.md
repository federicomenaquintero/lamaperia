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

Requirements
------------

You need these packages:

* python3

* python3-requests

* python3-gobject

* python3-cairo

* python3-pyproj

* pango

Quick Start
-----------

You need to tell La Mapería how to download tiles, and how to render
your map.

### Using my Mapbox style

At first, just run `./lamaperia.py`.  It will ask you if you want to
configure it, so say Y.  La Mapería puts its configuration file under
the ~/.config/lamaperia directory.

```
$ ./lamaperia.py 
La Mapería is not configured yet.
Would you like to configure La Mapería right now? [Y/n] y
```

You will be asked if you want to use TileStache, say N for now.  Later
we will see how to set up a personal tile cache with TileStache.  By
saying N here, La Mapería will download tiles directly from Mapbox.

```
Use TileStache? [Y/n] n
```

You will be asked for Mapbox access parameters.  At first you can
start using my public, printable style.  Later, if you have Mapbox
styles of your own, you can use them, too.

```
mapbox access token: [pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ]
mapbox username: [federicomenaquintero]
mapbox style id: [cil44s8ep000c9jm18x074iwv]
```

Just hit Enter after each of those questions, and they will use the
default values with my printable style.

### Configure La Mapería

Okay!  Now La Mapería complains mildly that you need to specify some
arguments when calling it.  It complains a lot for a little script,
doesn't it?

```
usage: lamaperia.py [-h] --config JSON-FILENAME --format STRING --output
                    FILENAME
lamaperia.py: error: the following arguments are required: --config, --format, --output
```

### For the impatient

To create a map, you need to create a little configuration file that
specifies how the map will look and which region it will show.  These
configuration files are in JSON format.

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
./lamaperia.py --config mymap.json --format pdf --output mymap.pdf
```

If everything works well, you'll get a mymap.pdf with the area where I
like to ride my bike.

Now you are ready to look at the `examples/` directory.  Most of the
files there look the same, and they just change the paper size and the
region to show in the map.

Configuration for the Map
-------------------------

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
the left, and two large divisions on the right:

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

#### Imperial scales

I'm not very familiar with maps with Imperial units.  The following produces
a map scale indicator with feet and miles, so that there are:

* 4 small-divisions with ticks at 1000 feet each, labeled just as "4000 ft" and "0".

* 3 large-divisions of 1 mile each, labeled as such.

```
    "scale-small-divisions-interval-m" : 304.8,
    "scale-num-small-divisions" : 4,

    "scale-large-divisions-interval-m" : 1609.344,
    "scale-num-large-divisions" : 3,

    "scale-small-ticks-m" : [ 0, "0",
			      304.8, "",
                              609.6, "",
			      914.4, "",
			      1219.2, "4000 ft" ],

    "scale-large-ticks-m" : [ 0, "0",
                              1609.344, "1",
                              3218.688, "2",
                              4828.032, "3 miles" ]
```

And the following produces small-divisions in quarter-mile increments, and large-divisions in 1 mile increments:

```
    "scale-small-divisions-interval-m" : 402.336,
    "scale-num-small-divisions" : 4,

    "scale-large-divisions-interval-m" : 1609.344,
    "scale-num-large-divisions" : 3,

    "scale-small-ticks-m" : [ 0, "0",
			      402.336, "",
			      804.672, "0.5",
			      1207.008, "",
			      1609.344, "1" ],

    "scale-large-ticks-m" : [ 0, "0",
                              1609.344, "1",
                              3218.688, "2",
                              4828.032, "3 miles" ]
```

If you know a better way to provide a printed map scale for Imperial
maps, I'd love to know about it!

Choosing a tile provider
------------------------

You can make La Mapería download tiles directly from Mapbox, or
preferably, you'll set up a TileStache cache to make downloading
faster if you regenerate similar map areas frequently.

### Using an arbitrary Mapbox style

If you don't have a Mapbox account, create one at 
https://www.mapbox.com/studio/signup/

Once you have a Mapbox Studio account and some styles in it, you can
select a style in Mapbox and then select the "Share, develop & use"
option.  You will see something like

```
Develop with this style

Style URL:     mapbox://styles/your_user_name/your_style_id
Access token:  your_access_token
```

Copy those strings.

You will have to delete ~/.config/lamaperia/config.json and start
`./lamaperia.py` like the first time you ran it.  Then you can paste
the strings from your Mapbox style into the configuration questions.

### Setting up a TileStache cache

TileStache (http://tilestache.org/) is a caching mechanism for
arbitrary sources of map tiles.  It runs on Python 2.

Download TileStache.  You don't need to install it; you can use it
with an example configuration file provided with La Mapería.

Go to `lamaperia/tilestache` and edit the tilestache-mapbox.cfg file
there.  Change this line:

```
    "path": "/home/federico/.cache/tilestache",
```

to something that makes sense for your machine.

Now, go to your downloaded `TileStache/scripts` directory and run

```
python tilestache-server.py --config=~/src/lamaperia/tilestache/tilestache-mapbox.cfg
```

using the correct configuration filename from your source directory
for La Mapería.

This will run the TileStache server with the same access parameters
for Mapbox that La Mapería uses by default (i.e. my printable map
style).

Now, delete your ~/.config/lamaperia/config.json and run
`./lamaperia.py` like the first time you ran it.  Say Y when asked if
you want to use TileStache.  The default URL and port for the
TileStache server should work.

The first time you generate a map, TileStache will download the
appropriate tiles.  If you regenerate that map, or make another map
that shares tiles with that first one, only the missing tiles will be
downloaded.  Magic!

If you need to discard part of the TileStache cache, for example, if you
modified data in OpenStreetMap, you can run

```
   cd ~/src/TileStache/scripts
   python tilestache-clean.py --layer=fmq-mapbox --bbox=19.5526 -96.917263 19.621099 -96.860778 --config=~/src/lamaperia/tilestache/tilestache-mapbox.cfg 14 15 16
```

The `--bbox` argument is the bounding box to discard in the cache.  La
Mapería prints the generated bounds of a map when you run it, so you
can just cut and paste those values there.

The last arguments (`14 15 16`) are the zoom levels to discard.  These
correspond to the zoom levels from your JSON map files for La Mapería.

Feedback
--------

I'm reachable at Federico Mena Quintero <federico@gnome.org>.

Enjoy La Mapería!
