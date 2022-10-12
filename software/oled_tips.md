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
|contrast|contrast|Changes the contrast based on a value
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
