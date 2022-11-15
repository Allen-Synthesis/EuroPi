# OLED Tips

The OLED (Organic Light-Emitting Diode) used in the EuroPi is a 128x32px 0.91" display, which uses the SSD1306 driver controller.  
The I²C protocol is used to communicate with the display, and the *micropython-ssd1306* module is used to provide this ability to communicate using useful commands.  
The display is stored as a Python object, named *oled*, and you use methods to perform a function, such as:
```
oled.fill(0)
```
The pixels are indexed with (0, 0) at the top left, and (127, 31) at the bottom right.

## Available Methods

| Method | Parameters | Function |
| ------ | ---------- | -------- |
|text|string, x, y, colour|Writes the string text at (x, y)|
|fill|colour|Fills the display either white (1) or black (0)|
|line|x1, y1, x2, y2, colour|Draws a 1px wide line between (x1, y1) and (x2, y2) in the specified colour|
|hline|x, y, length, colour|Draws a horizontal wide line starting at (x, y) with specified length and colour|
|vline|x, y, length, colour|Draws a vertical wide line starting at (x, y) with specified length and colour|
|rect|x, y, width, height, colour|Draws a rectangle starting at (x, y) with specified width, height, and outline colour|
|fill_rect|x, y, width, height, colour|Draws a rectangle starting at (x, y) with specified width, height, and fill colour|
|blit|buffer, x, y|Draws a bitmap based on a buffer, starting at (x, y)
|scroll|x, y|Scrolls the contents of the display by (x, y)
|invert|colour|Inverts the display
|contrast|contrast|Changes the contrast based on a value between 0 and 255
|show||Updates the physical display with the contents of the buffer

### Using .show()
One thing to make sure of is that you use oled.show() whenever you need to update the display.  
The reason this isn't automatic is because the actual .show() method is quite CPU intensive, so it allows your program to run much faster if you complete all of your buffer write operations (text, lines, rectangles etc) and then only .show() once at the end.

## Extra Functions from europi.py

There are also some methods provided in the EuroPi library, which are designed to make certain common uses of the OLED easier.  
These can be accessed the same way as the predefined methods listed above, and you can even add your own to your own europi.py file if you wish.

| Method | Parameters | Function |
| ------ | ---------- | -------- |
|centre_text|string|Takes a string of up to 3 lines separated by '\n', and displays them centred vertically and horizontally|
|clear||Clear the display upon calling this method. If you just need to clear the display buffer, use `oled.fill(0)`.

### `centre_text` example

*Python Program*

```python
from europi import *

oled.centre_text("this text\nhas been\ncentred")
```

*OLED Result*

![imgur](https://i.imgur.com/Elljlt1.jpg)

## Custom images

  Custom images can be displayed using the blit function.
 ```python
from europi import *
# The black and white image needs to be stored as bytearray:
img=b'\x00\x00\x00\x01\xf0\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x02\x08\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x04\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc4\x04\x00\x18\x00\x00\x00p\x07\x00\x00\x00\x00\x00\x00\x0c$\x02\x00~\x0c\x18\xb9\x8c8\xc3\x00\x00\x00\x00\x00\x10\x14\x01\x00\xc3\x0c\x18\xc3\x060c\x00\x00\x00\x00\x00\x10\x0b\xc0\x80\x81\x8c\x18\xc2\x020#\x00\x00\x00\x00\x00 \x04\x00\x81\x81\x8c\x18\x82\x02 #\x00\x00\x00\x00\x00A\x8a|\x81\xff\x0c\x18\x82\x02 #\x00\x00\x00\x00\x00FJC\xc1\x80\x0c\x18\x82\x02 #\x00\x00\x00\x00\x00H\x898\x00\x80\x0c\x18\x83\x060c\x00\x00\x00\x00\x00S\x08\x87\x00\xc3\x060\x81\x8c8\xc3\x00\x00\x00\x00\x00d\x08\x00\xc0<\x01\xc0\x80p7\x03\x00\x00\x00\x00\x00X\x08p \x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00#\x88H \x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00L\xb8& \x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\x91P\x11 \x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\xa6\x91\x08\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9\x12\x84`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x12C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x11 \x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00H\x0c\x90\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x12\x88\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x12F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x10A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10  \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08  \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04@@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
imgBA = bytearray(img)
# Then a small FrameBuffer needs to be created that shows the image:
imgFB = FrameBuffer(imgBA, 128, 32, MONO_HLSB)
# Finally the small FrameBuffer can be blit anywhere onto the display FrameBuffer
oled.blit(imgFB,0,0)
oled.show()
```
To generate the bytearray string from an jpg file this tool can be used:

https://github.com/novaspirit/img2bytearray

Make sure your jpg has the right size and you use the same size when you run this tool and in the micropython code.
Images will be inverted. So a black pixel on the jpg will be bright on the oled

## Burn in
If a script is left running for a long period of time, it can burn that screen into the oled and leave ghost images.
To avoid this it is recommended to not leave the EuroPi screen on for very long periods of time with with something static on the display.
If you write a script consider adding a 'screensaver' function (for example clear the screen if there was no user interaction for an extended time period).
