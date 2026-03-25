BoreMapper
==========

A woodwind instrument makers' app for mapping the profile of **split bore** instruments, like Native American flute or forest flute.

It can be used with routed as well as hand-chiseled bore, and is especially handy for an irregular bore.


Motivation
----------

When crafting a woodwind instrument, it is often important to calculate its effective bore diameter, so that we can lay out its finger holes properly, for example.

Yet split-bore flutes, after glued together, rarely have a perfectly circular bore, so the math gets more complex.
Even more so when the router bit is semi-elliptical rather than semi-circular, or when the groove width/depth is irregular.

How great would it be to have an app that would calculate the effective bore diameter for us.


Usage
-----

By measuring the width and height (depth) of the groove at various positions (in both *bottom* and *top* part), the app reconstructs bore shape at each of these positions, and calculates its area-equivalent diameter.
The calculated diameters can be exported into `WIDesigner <https://github.com/edwardkort/WWIDesigner>`_ application.

- For a **routed bore**, it is advisable to also specify dimensions of the cutter bit used, so that the groove shape can be determined more accurately.
- For a **hand-chiseled bore**, leave cutter dimensions at their default values - the groove is then assumed to have an arc shape.


Tools Needed
------------
- Calipers
- Depth Caliper
- Convenient ruler or tape measure

**Recommendation:** To best utilize the app, it is recommended to use calipers with a **data output** feature. By enabling *Voice Hints* option in the app, it keeps reading the current position as you measure. This makes the process much smoother, as you don't need to keep checking the screen.


Current Limitations
-------------------

- Export to WIDesigner is done by *copy & paste* of the generated XML chunk
- Bore is assumed to be split horizontally (halves are named *bottom* and *top*, and displayed in this orientation)


Features
--------

- Voice hints for smoother measurement flow
- Global corrections of measured data
- Cross-sectional diagrams
- `WIDesigner <https://github.com/edwardkort/WWIDesigner>`_ export