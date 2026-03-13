BoreMapper
==========

A woodwind instrument makers' app for mapping the bore profile of woodwind instruments with a **split bore**, like Native American flute or forest flute.

It can be used with routed as well as hand-chiseled bore, and is especially handy for bores with irregular profile.


Motivation
----------

It is often important to calculate the effective bore diameter of a woodwind instrument to lay out its finger holes properly.

Yet split-bore flutes rarely have a perfectly circular bore after glued together, so the math gets more complex.
Even more so when the router bit is semi-elliptical rather than semi-circular, or the groove width/depth is irregular.

How wonderful would it be to have an app that would take some basic dimensions and calculate an area-equivalent bore diameter for us.


Usage
-----

By measuring the width and height (depth) of the groove at various positions (in both *bottom* and *top* part), the app reconstructs bore shape at each of these positions, and calculates its area-equivalent diameter.
The calculated diameters can be exported into `WIDesigner <https://github.com/edwardkort/WWIDesigner>`_ application.

- For **routed bore**, it is recommended to also specify dimensions of the cutter bit used, so that the groove shape can be determined more accurately.
- For **hand-chiseled bore**, leave cutter dimensions at their default values - the groove is then assumed to have an arc shape.


Tools Needed
------------
- Calipers
- Depth Caliper
- Convenient ruler or tape measure

**Recommendation:** To best utilize the app, it is recommended to use calipers with **data output** feature. By enabling *Voice Hints* option in the app, it keeps reading the current position as you measure. This makes the process much smoother, as you don't need to keep checking the screen.


Current Limitations
-------------------

- Only *mm* units are currently supported
- Export to WIDesigner application is done by *copy & paste* of the generated XML chunk
- Horizontal bore split is assumed (for vertical split, the parts should be named left/right rather than bottom/top)


Features
--------

- Voice hints for smoother measurement flow
- Global corrections of the measured data
- Cross-sectional diagrams
- `WIDesigner <https://github.com/edwardkort/WWIDesigner>`_ export