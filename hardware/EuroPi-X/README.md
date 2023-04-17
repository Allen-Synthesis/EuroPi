# EuroPi X

The EuroPi X is an improved hardware version of the EuroPi. Its exact feature set is yet to be decided, but likely additions are more inputs, more outputs, better noise performance for inputs, better accuracy for outputs, a larger display, and larger flash storage.

Suggested features:
- RGB LEDs for outputs
  - [Neopixels](https://www.adafruit.com/product/4492?gclid=Cj0KCQjw2cWgBhDYARIsALggUhp21QpzSRPmMwkA5GLrfMsx_jSPfgyTrgrEi0MlV2bsC2WGbknoDSoaAqggEALw_wcB)?
  - Colour matches output type e.g. red for gate, blue for CV, green for 1v/oct
  - Colour determined automatically in code when a method is used, e.g. cv1.on() would automatically set it to red as a gate type
- DAC outputs (>=12 bit)
  - [MCP4728](https://shop.pimoroni.com/products/adafruit-mcp4728-quad-dac-with-eeprom-stemma-qt-qwiic?variant=31458498412627&currency=GBP&utm_source=google&utm_medium=cpc&utm_campaign=google+shopping?utm_source=google&utm_medium=surfaces&utm_campaign=shopping&gclid=Cj0KCQjwtsCgBhDEARIsAE7RYh3qANxNiQCtKDUFhGal1OTP4WOT_NSxUyUTKL1Pj_3x2VDyPnRayScaAk5DEALw_wcB)? 12 bit, 4 channel
  - Bipolar https://tinyurl.com/2abku7y3, jumper on the back of the module to set the mode, GPIO detects mode to allow code adjustments:

    ![image](https://user-images.githubusercontent.com/79809962/232499051-03726a7a-2504-42e1-a2b6-9dd00e95a89b.png)

- More inputs
  - 4 inputs can fit in 8HP
- Higher performance CV inputs
  - External ADC, maybe with higher resolution
  - Separate analogue and digital power supplies using RP2040 AGND
- Ability to use +5V rail instead of internally generated
  - 16 pin header
  - Automatically use +5V rail if present, default to internally generated if not
- Make unused GPIO and USB signals accessible from the back
  - Keep one I2C/SPI bus unused so users don't have to worry about address clashes
  - Make sure USB signals are length matched
- Larger display (128x64 or larger)
  - [SSD1306](https://www.buydisplay.com/serial-spi-1-3-inch-128x64-oled-display-module-ssd1306-white-on-black) without breakout board (use Izaak's in progress board?) 
- Bipolar inputs
- Bipolar outputs
- Programmable I/O to allow unipolar or bipolar usage
  - Analogue switch IC? [DG4051 octa analog switch](https://www.mouser.co.uk/ProductDetail/Vishay-Siliconix/DG4051EEQ-T1-GE3?qs=367PjNmvCmmPtnHZ5hoXyA%3D%3D)
- Front access USB
- Front access reset and bootsel
- MicroSD slot for increased storage
- Increased flash by default
- Automatic detection of variant i.e. X or normal hardware
  - One GPIO tied to 3.3V, module detects it's an X if GPIO is high
  - Also set in config settings if module can't detect automatically
