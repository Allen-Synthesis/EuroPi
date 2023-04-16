# Bill of Materials

In addition to the Front Panel, Jack PCB, and Pico PCB (bought from Allen Synthesis or a third-party supplier), you will need the following components to complete your build.
You will also need one 3.5mm cable (normal Eurorack patch cable) to perform the calibration process.  
  
Please note that a few of these are multi-packs of components, and there may well be cheaper alternatives if you are doing a single build, so as long as the specification is the same you can get any of these components from any supplier most accessible to you.

| Component | Quantity | Value | Description | Suggested Supplier
|-|-|-|-|-|
| R1 - R12, R19 - R20 | 14 | 1k | 1 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-1k/resistor-0-25w-1-1k/dp/RE03722)
|R13 - R18 | 6 | 4.7k | 4.7 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-4k7/resistor-0-25w-1-4k7/dp/RE03757)
| R21 - R23 | 3 | 22k | 22 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-22k/resistor-0-25w-1-22k/dp/RE03743)
| R24 - R26 | 3 | 10k | 10 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-10k/resistor-0-25w-1-10k/dp/RE03723)
| R27 - R34 | 8 | 100k | 100 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-100k/resistor-0-25w-1-100k/dp/RE03724)
| R35 - R40 | 6 | 220k | 220 Kiloohm Resistor | [CPC](https://cpc.farnell.com/unbranded/mf25-220k/resistor-0-25w-1-220k/dp/RE03744)
| C1 - C2 | 2 | 1uF | 1 Microfarad Capacitor (Polarised)| [CPC](https://cpc.farnell.com/multicomp/mcmhr50v105m4x7/capacitor-1uf-50v-radial-105-deg/dp/CA08237)
| C3 - C14 | 12 | 100nF | 100 Nanofarad Capacitor (Non-Polarised)| [CPC](https://cpc.farnell.com/multicomp/mcrr50104x7rk0050/capacitor-100nf-50v/dp/CA06296)
| C15 - C16 | 2 | 10uF | 10 Microfarad Capacitor (Polarised)| [CPC](https://cpc.farnell.com/panasonic/eeueb1j100s/capacitor-10uf-63v-5x11mm/dp/CA08350)
| D1 - D4 | 4 | 1N5817 | Schottky Diode | [CPC](https://cpc.farnell.com/multicomp-pro/1n5817/schottky-rectifier-1a-20v-do-204al/dp/SC15528)
| LED1 - LED6 | 6 | L-424HDT | 3mm LED | [CPC](https://cpc.farnell.com/kingbright/l-424hdt/led-flat-top-3mm-red/dp/SC11541)
| VR1 - VR2 | 2 | 10k | 10 Kiloohm Linear Rotary Potentiometer | [CPC](https://cpc.farnell.com/alps/rk09k11310kb/potentiometer-10k-lin/dp/RE04560), [Thonk](https://www.thonk.co.uk/shop/alpha-9mm-pots-vertical-t18/) (B10K - T18 Shaft - Alpha Vertical Potentiometer)
| SW1 - SW2 | 2 | D6RXX F1 LFS | C&K Tactile Switch (Non-Illuminated) | [Thonk](https://www.thonk.co.uk/shop/radio-music-switch/), [Mouser (Black)](https://www.mouser.co.uk/ProductDetail/CK/D6R90F1LFS?qs=WS%2FiepCTwPDejJXcQ7Ir1g%3D%3D&countrycode=US&currencycode=USD)
| OLED1 | 1 | 0.91" SSD1306 | I2C OLED Display | [CPC](https://cpc.farnell.com/winstar/wea012832fwpp3n00000/oled-display-128x32-white-i2c/dp/SC15661), [The Pi Hut](https://thepihut.com/products/0-91-oled-display-module)
| J1 - J8 | 8 | PJ398SM | Thonkiconn 3.5mm Mono Jack | [Thonk](https://www.thonk.co.uk/shop/thonkiconn/), [Banananuts](https://www.thonk.co.uk/shop/bananuts/), [Cosmonuts](https://www.thonk.co.uk/shop/cosmonuts/)
| CONN0 | 2 (pairs) | 20x1 2.54mm | Pico Connection Header (Male + Female) | [Male](https://cpc.farnell.com/harwin/m22-2012005/header-vertical-1row-20way/dp/CN14644), [Female](https://cpc.farnell.com/multicomp/2212s-20sg-85/socket-pcb-1-row-20way/dp/CN14539)
| CONN1 - CONN4 | 2 (pairs) | 4x2 2.54mm | PCB Connection Header (Male + Female) | [Male](https://cpc.farnell.com/harwin/m20-9980445/header-2row-4way/dp/CN14381), [Female](https://cpc.farnell.com/multicomp/2214s-08sg-85/socket-pcb-2-54mm-2-row-vert-8way/dp/CN18449)
| CONN5 | 1 | 4x1 2.54mm | I2C Header (Male) | [CPC](https://cpc.farnell.com/multicomp/2211s-04g/header-1-row-vert-4way/dp/CN14489)
| CONN6 | 1 | 5x2 2.54mm | Eurorack Power Header (Shrouded) | [CPC](https://cpc.farnell.com/3m/n2510-6002rb/2-54mm-header-straight-10-way/dp/CN20355)
| TL074-1 - TL074-2 | 2 | TL074 DIP | Quad Operational Amplifier (+ Socket) | [Op-Amp](https://cpc.farnell.com/texas-instruments/tl074acn/ic-op-amp-quad-jfet-dip14/dp/SC16602), [Socket](https://cpc.farnell.com/unbranded/mc-2227-14-03-f1/socket-ic-dil-0-3-tube-34-14way/dp/SC08125)
| MCP6002 | 1 | MCP6002 DIP | Dual Operational Amplifier (+ Socket) | [Op-Amp](https://cpc.farnell.com/microchip/mcp6002-i-p/ic-op-amp-1-8v-1mhz-dual-pdip8/dp/SC17118), [Socket](https://cpc.farnell.com/multicomp/spc15494/dip-socket-8pos-2row-2-54mm-th/dp/SC15358)
| Q1 | 1 | 2N3904 | NPN Transistor | [CPC](https://cpc.farnell.com/multicomp-pro/2n3904/transistor-npn-to-92/dp/SC15978)
| 7805 | 1 | L7805ABV | 5V Linear Voltage Regulator | [CPC](https://cpc.farnell.com/stmicroelectronics/l7805abv/ic-v-reg-5v/dp/SC10586)
| | 1 | 11mm | M2.5 PCB Standoff + 2 Screws | [Standoff](https://cpc.farnell.com/ettinger/05-02-113/spacer-hex-m2-5-11mm-length-brass/dp/PC01763), [Screws](https://cpc.farnell.com/unbranded/pp2m5-6/screw-pan-pozi-m2-5-x-6mm-100pk/dp/FN02140)
| | 2 | T18 Shaft | Knobs | [Thonk](https://www.thonk.co.uk/shop/1900h-t18/) NOTE: If you buy D-Shaft potentiometers, the knobs must be 'Reverse-D-Shaft' type.
| | 1 | 10 - 16 Pin | Eurorack Power Cable | [Thonk](https://www.thonk.co.uk/shop/eurorack-power-cables/)
| | 1 | | Micro USB Cable (Capable of Data Transfer) | [CPC](https://cpc.farnell.com/pro-signal/psg91562/lead-usb-a-male-micro-b-male-black/dp/CS32732), [The Pi Hut](https://thepihut.com/products/usb-to-micro-usb-cable-0-5m)
| | 1 | | Raspberry Pi Pico | [The Pi Hut](https://thepihut.com/products/raspberry-pi-pico), [CPC](https://cpc.farnell.com/raspberry-pi/raspberry-pi-pico/raspberry-pi-pico-rp2040-mcu-board/dp/SC17106)

#### Note about OLED
The OLED has two suppliers listed, each with different pin configurations. The module supports either of these two configurations (the most common), but no others, so make sure that the one you buy, wherever you source it, has one of these two configurations.  
It also *must* be 36mm or less. There are some displays which are 38mm wide, which will not only not fit within the width of the module, but will also leave the display off-centre in relation to the panel cutout. You can check the datasheet of any display before you buy to determine the width, but both of the displays listed in the BOM above are the correct 36mm.

![OLED Pin Configurations](https://user-images.githubusercontent.com/79809962/145800121-2c88d73b-b4d2-4196-baa1-8628dc327467.png)
![OLED Width](https://user-images.githubusercontent.com/79809962/153423641-4242a637-bd0d-493f-a1f7-94823b07cfd7.png)
