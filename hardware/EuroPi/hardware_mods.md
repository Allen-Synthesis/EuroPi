# Hardware Mods

This file documents some common hardware modifications to EuroPi. These modifications are wholly
at your own risk; if performed wrong they could cause damage to your module!

## Alternative to OLED jumper wires

Instead of [soldering jumper wires](/hardware/EuroPi/build_guide.md#oled-configuration) to configure
the OLED, you can instead install a 2x4 bank of headers and use 4 jumpers. This makes it easy to
reconfigure the OLED connection, which may be useful if you ever need to replace the display.

TODO: picture here

_Header pins and jumpers used in the CPC orientation_

## Reducing analogue input noise

The original analogue input stage, as designed by Émilie Gillet (of Mutable Instruments fame) includes
a 1uF capacitor located in parallel with the final resistor:

<img src="https://private-user-images.githubusercontent.com/9308899/389262067-cbc6ca9a-32d0-4bef-8f39-e4c36ff0cb06.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzY1MzE2ODMsIm5iZiI6MTczNjUzMTM4MywicGF0aCI6Ii85MzA4ODk5LzM4OTI2MjA2Ny1jYmM2Y2E5YS0zMmQwLTRiZWYtOGYzOS1lNGMzNmZmMGNiMDYucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDExMCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTAxMTBUMTc0OTQzWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9OGE0NGM5ZDQxNTExNzc3ZjRmYmVkMzQxZGY2YTcyMjFlYzFhNmJkN2MzYjA5NjYwM2RkYTU5NTUwYWM3NWYxNCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.GPVjD3K0nnWzSCNSkwAPMJc1BbZ21tsMroKO2Zjgsjw" width="420">

_The input stage of Mutable Instruments Braids. Note the `1n` capacitor in the upper-right._

If you find your EuroPi's V/Oct outputs are incorrect, or are seeing an undesirable amount of jitter on
`AIN`, you can add a 1uF capacitor in parallel with `R23`. The easiest way to do this is to _carefully_
solder the 1uF capacitor directly to the back-side of `R23`, as shown below:

<img src="https://private-user-images.githubusercontent.com/9308899/390605531-ca992dc2-8382-46b9-866a-64bcaf300806.jpg?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzY1MzE2ODMsIm5iZiI6MTczNjUzMTM4MywicGF0aCI6Ii85MzA4ODk5LzM5MDYwNTUzMS1jYTk5MmRjMi04MzgyLTQ2YjktODY2YS02NGJjYWYzMDA4MDYuanBnP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDExMCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTAxMTBUMTc0OTQzWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MzQ3NDMzNmFlMWZhNzhlMzhhOTlkZWNhZWY2Njc0NDA3ZDM5MThmNTdiOGVjYjA1OWU4YzYzZWFjNTdiNDJhNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.j-L3r8DzCIqud7ooEQB8zhgxahz3Bi-0tRE-3pV6HJk" widht="360"> <img src="https://private-user-images.githubusercontent.com/9308899/390605507-5fd06824-c6f6-4666-a37a-74d30cf83348.jpg?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzY1MzE2ODMsIm5iZiI6MTczNjUzMTM4MywicGF0aCI6Ii85MzA4ODk5LzM5MDYwNTUwNy01ZmQwNjgyNC1jNmY2LTQ2NjYtYTM3YS03NGQzMGNmODMzNDguanBnP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDExMCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTAxMTBUMTc0OTQzWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDM0ZmEwMDlkYTdjMjY5YTgyZGI2YTM3ZTU2MDkxNDZjMjU1MmUwMWUwZGE5MzU2Mzc2MmUzY2IyMjFhNTc0MiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.M43lAd0ePAeJ1lMwEaZ7-bqb844vl9ZRTXrHBjv0qeA" width="360">

_A 1uF capacitor soldered to the back-side of the EuroPi PCB, in parallel with `R23`_

After soldering the 1uF capactor in place, you should [recalibrate EuroPi](/software/firmware/tools/calibrate.md).
