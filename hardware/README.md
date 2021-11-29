# Hardware Specifications

### Note:
The PCB files have been temporarily removed to prevent people from creating their own before the files have been tested. I do not want to risk anyone creating something based on unfinished designs. Rest assured once they have been tested, the files will be available in this folder.

## Outputs
- 1k Output Impedance
- RC filter smoothed PWM
- 33Hz Maximum usable frequency (without changing RC values)
- 0.000176V Maximum ripple peak-to-peak
- 0.0108s Settle time from 0% to 90% duty cycle
- 0-10V

## Analogue Input
- 100k Input Impedance
- 0-12V Readable Range
- Protected for ±36V (TL074 limits, MCP6002 will always clip to ±3.3V)

## Digital Input
- 100k Input Impedance
- 0.8V threshold to read as high

## OLED
- SSD1306 0.91"
- 128 x 32 pixels
- I2C Protocol
