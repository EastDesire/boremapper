BoreMapper
==========

A woodwind instrument makers' app for mapping a profile of **split-bore** instruments (like Native American flute or forest flute).

It can be used with routed as well as hand-chiseled bore, and is especially handy for an irregular bore.


Motivation
-----

When crafting a woodwind instrument, it is often important to calculate its effective bore diameter, so that we can lay out the finger holes properly, for example.

Yet split-bore flutes, after glued together, rarely have a perfectly circular bore. The math gets more complex when the router bit is semi-elliptical rather than semi-circular, or when the groove width/depth is irregular.

How great would it be to have an app that would calculate the effective bore diameter for us.


Usage
-----

After measuring the width and height (depth) of the groove at various positions (in both *bottom* and *top* part), the app reconstructs bore shape at each of these positions, and calculates its area-equivalent diameter.
The calculated diameters can be exported into `WIDesigner <https://github.com/edwardkort/WWIDesigner>`_ application.

- For a **routed bore**, it is advisable to also specify dimensions of the cutter bit used, so that the groove shape can be determined more accurately.
- For a **hand-chiseled bore**, leave the cutter dimensions at their default values - the groove is then assumed to have an arc shape.


Tools Needed
-----

- Calipers
- Depth caliper
- Convenient ruler or tape measure

**Recommendation:** To best utilize the app, it is recommended to use calipers with a **data output** feature. By enabling *Voice Hints* option in the app, it keeps reading the current position as you measure. This makes the process much smoother, as you don't need to keep checking the screen.


Exporting to WIDesigner
-----

- In the menu, click *Export* -> *WIDesigner...*
- Ensure *WIDesigner Length Type* is set to the units you use in WIDesigner
- If needed, you can offset all bore points using *Bore Origin* field. Otherwise leave it at 0.
- In WIDesigner, in your instrument's tab, add a sufficient number of rows to the *Bore Points* table
- In BoreMapper, copy the *Positions* column to clipboard and paste it into *Bore Points* table. Then do the same with *Diameters*.

**Note:** Alternatively, instead of employing the *Bore Points* table, you can just paste the generated `<borePoint>` blocks over the existing ones in your instrument's XML editor (the Vu button in WIDesigner toolbar). Use this method only if you know what you are doing.


Current Limitations
-----

- Bore is assumed to be split horizontally (halves are named *bottom* and *top*, and displayed in this orientation)
- Only round cutter shape is supported (circular or elliptical). This, however, covers most of the traditionally used router bits as well as semi-elliptical grooves made with chisel.


Features
-----

- Voice hints for smoother measurement flow
- Cross-sectional diagrams, profile diagrams
- WIDesigner export