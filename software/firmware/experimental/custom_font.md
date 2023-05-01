Custom Font support
===================

The `CustomFontWriter` class is adapted from https://github.com/peterhinch/micropython-font-to-py/tree/master/writer.

How to generate custom fonts :
------------------------------

To generate font files, use https://github.com/peterhinch/micropython-font-to-py/blob/master/font_to_py.py.

The fonts in this folder have been generated from TTF files downloaded from with https://www.wfonts.com/.

The commands are :

    python3 font_to_py.py FreeSans.ttf 14 freesans14.py -x
    python3 font_to_py.py FreeSans.ttf 17 freesans17.py -x
    python3 font_to_py.py FreeSans.ttf 20 freesans20.py -x
    python3 font_to_py.py FreeSans.ttf 24 freesans24.py -x

The -x option is important to have the font horizontally mapped.

How to use the CustomFontWriter class :
---------------------------------------

See `software/contrib/custom_font_demo.py` for usage examples.

To test the CustomFontWriter in your code you can simply replace :

    from europi import oled

with :

    from experimental import custom_font
    oled = custom_font.Display(sda=0, scl=1)

By default, custom_font.Display will use the 8x8 pixel monospaced font.

To use custom fonts, import them : 

    from experimental import freesans20

and pass them as the font argument to any custom_font.Display methods :

    oled.centre_text("20", font=freesans20)

To know how much space a text will occupy on screen, use : 

    w_pixels = oled.text_width("my text", font=freesans20)
    h_pixels = oled.text_height("my text", font=freesans20)

