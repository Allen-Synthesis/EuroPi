# Build Guide

#### Introduction
This document will go through the assembly of the EuroPi module.  
If you have bought only a Panel + PCB kit, you will need to also buy all of the components found in the [bill of materials](/hardware/EuroPi/bill_of_materials.md).  
  
This build is entirely through-hole (not even any pre-soldered SMD components!) so don't worry if you're fairly new to DIY, these instructions should be all you need to make your module.  
  
This guide should explain every step in enough detail, but there are some things left out for simplicity's sake, such as the fact that after each step any long legs will need to be snipped using your wire snips or scissors. This is only necessary for components with long legs, so resistors, capacitors, and LEDs. You don't need to snip anything off any of the headers, the 7805, the jacks, potentiometers, or IC sockets.  
 
#### Skiff Friendly Build 
There are two options for some of the build, one of which makes the module more skiff friendly (37mm deep as opposed to 45mm). If you wish to make the thinner version, simply click the links that say [Skiff Friendly Option](), and follow the instructions to guide you back into the normal build at the right points. Simply ignore these links if you don't mind the module being slightly deeper.

![1 all](https://user-images.githubusercontent.com/79809962/147943816-3ac2098c-14cf-4fac-8896-1ba1f2c7397f.jpg)
  
## Required tools
- Soldering Iron + Solder
- Wire Snips / Scissors
- Multimeter (Very nice to have but non-essential)

![2 tools](https://user-images.githubusercontent.com/79809962/147944628-6954b9f4-4f29-4064-8ad4-35a578848826.jpg)

## Preparation

#### If not already soldered, solder the headers to the Pico so that they are on the opposite side to the black integrated chips. It may help to push it into a breadboard to make sure the headers are straight
![_DSC2386](https://user-images.githubusercontent.com/79809962/148646823-2da452c7-3936-41cf-8018-bba5de6bef43.jpg)



## Pico PCB

The 'Pico PCB' is the PCB with the outline of the Pico on it.  
The 'front' of the Pico PCB is the side with the actual Raspberry Pi Pico on it, and the 'back' is the side with the transistor outline on it.

|Front|Back|
|-----|----|
|![DSC2404](https://user-images.githubusercontent.com/79809962/148678993-6827be45-b70a-4fd9-9905-f2933294647a.jpg)|![DSC2405](https://user-images.githubusercontent.com/79809962/148679010-572c4134-9486-4192-8155-193a9f78333f.jpg)|

#### Required Components for Pico PCB
|Component|Quantity|
|---------|--------|
|1k Resistor|6|
|22k Resistor|3|
|100k Resistor|8|
|220k Resistor|6|
|10k Resistor|3|
|Schottky Diode|4|
|100nF Capacitor|10|
|14 Pin IC Socket|2|
|8 Pin IC Socket|1|
|NPN Transistor|1|
|1uF Capacitor|2|
|4x2 Female Header|2|
|Shrouded Power Header|1|
|4x1 Male Header|1|
|20x1 Female Pico Header|2|
|10uF Capacitor|2|

---

### Resistors

#### Solder the 1k resistors to the front (R1, R2, R3, R4, R5, R6)
![_DSC2333](https://user-images.githubusercontent.com/79809962/148646413-a5415b17-0669-4a59-b485-ea4cdfa58bd3.jpg)
![_DSC2335](https://user-images.githubusercontent.com/79809962/148646432-1523114d-7602-43a3-9e0a-4f20e2000619.jpg)



#### Solder the 22k resistors to the front (R21, R22, R23)
![_DSC2338](https://user-images.githubusercontent.com/79809962/148646442-051cc03f-4697-4cfe-a3e4-f115df2dbe54.jpg)


#### Solder the 100k resistors to the front (R28, R29, R30, R31, R32, R33, R34)
![_DSC2339](https://user-images.githubusercontent.com/79809962/148646446-d705c559-2af5-4e06-a172-889cb2d67713.jpg)


#### Solder the 220k resistors to the front (R35, R36, R37, R38, R39, R40)
![_DSC2340](https://user-images.githubusercontent.com/79809962/148646450-b42c46fa-61fe-4ca5-bc31-0c01bfc67af8.jpg)


#### Solder the 10k resistors to the back (R24, R25, R26)
![_DSC2341](https://user-images.githubusercontent.com/79809962/148646454-79eb31b6-bb91-49f3-9f5b-2a613e66cca4.jpg)


#### Solder the 100k resistor to the back (R27)
![_DSC2342](https://user-images.githubusercontent.com/79809962/148646458-ad031bd1-d5ca-4719-a0f1-947e0d4e2e0a.jpg)

---

### Diodes

#### Solder the Schottky diodes to the front (D2, D3, D4), taking care of the polarity
![_DSC2343](https://user-images.githubusercontent.com/79809962/148646464-84977e13-0376-496c-a1bd-fc8b9a17d868.jpg)


#### Solder the Schottky diode to the back (D1), taking care of the polarity
![_DSC2344](https://user-images.githubusercontent.com/79809962/148646468-ba371a92-ff31-4736-8c7c-fb2ca1f17adc.jpg)

---

### Small Capacitors

#### Solder the 100nF capacitors to the front (C3, C4, C5, C6, C9, C10, C11, C12, C13, C14)
![_DSC2345](https://user-images.githubusercontent.com/79809962/148646472-d1251dea-80df-4390-86ca-999f373e6b00.jpg)

---

### IC Sockets

#### Solder the 14 Pin IC sockets to the front (TL072-1, TL072-2), lining up the notch with the white square on the PCB
![_DSC2346](https://user-images.githubusercontent.com/79809962/148646476-41c06762-e73e-4786-ac0d-0b806e3fd1f6.jpg)


#### Solder the 8 pin IC socket to the front (MCP6002), lining up the notch with the white square on the PCB
![_DSC2347](https://user-images.githubusercontent.com/79809962/148646483-da9f3b0f-4aea-424e-823c-ac6e7a78453a.jpg)

---

### Transistor

#### Solder the NPN transistor to the back (Q1), lining up the flat edge with the line on the PCB
![_DSC2348](https://user-images.githubusercontent.com/79809962/148646486-14f6309a-ea8c-4bee-8c94-d4c7b921d6af.jpg)

---

### Medium Capacitors

#### Solder the 1uF capacitors to the front (C1, C2), taking care of the polarity. The white stripe on the capacitor lines up with the stripe on the PCB
![_DSC2349](https://user-images.githubusercontent.com/79809962/148646495-35dfc9f5-1854-453d-9198-1f60a5cc18f1.jpg)

---

### Headers

#### Solder the female headers to the back
![_DSC2350](https://user-images.githubusercontent.com/79809962/148646500-13df4d33-5d84-456d-b054-be358e716849.jpg)


#### Solder the shrouded power header to the front
![_DSC2351](https://user-images.githubusercontent.com/79809962/148646504-e379a3b3-d3a7-4c9a-9a7f-121275f740f5.jpg)


#### Solder the I²C header to the front
![_DSC2352](https://user-images.githubusercontent.com/79809962/148646508-d44a06fb-7a40-4acd-96ce-360de89eb10a.jpg)



[Skiff Friendly Option](skiff_friendly_instructions.md#step-1)

#### Push the female Pico headers onto the Pico itself
![_DSC2355](https://user-images.githubusercontent.com/79809962/148646518-ea8e78d0-0eac-4c52-a066-faef7229b62f.jpg)


#### Press this new assembly onto the footprint on the PCB
![_DSC2356](https://user-images.githubusercontent.com/79809962/148646530-7f750952-8b80-430b-ab41-4a9a215a94a4.jpg)


#### Solder the female headers from the back
![_DSC2357](https://user-images.githubusercontent.com/79809962/148646542-447cbf0c-5ecc-44a4-8ec4-8acdbe778758.jpg)


#### Remove the Pico from the female headers
![_DSC2358](https://user-images.githubusercontent.com/79809962/148646556-57eafa92-572d-4bbf-8f6d-6cc406054a1a.jpg)
![_DSC2359](https://user-images.githubusercontent.com/79809962/148646560-23bce840-6db8-463b-95fb-cd9e1df0993c.jpg)


---

### Large Capacitors

#### Solder the 10uF capacitors to the front (C15, C16), taking care of the polarity. The white stripe on the capacitor lines up with the stripe on the PCB
![_DSC2360](https://user-images.githubusercontent.com/79809962/148646579-7bc26aa0-817f-4a3e-bb92-e03fa232a60a.jpg)

---

### 7805

[Skiff Friendly Option](skiff_friendly_instructions.md#step-2)

#### Solder the 7805 power regulator to the front, with the metal side in line with the white stripe on the PCB
  
![_DSC2361](https://user-images.githubusercontent.com/79809962/148646604-5add0541-0e27-4e8b-b558-8c35df24b997.jpg)

---

## Jack PCB

The 'Jack PCB' is the remaining board, with the outlines for the front panel components.  
The 'front' of the Jack PCB is the side with the OLED, jack, and button outlines, and the 'back' is the side with the OLED configuration diagram.

|Front|Back|
|-----|----|
|![DSC2406](https://user-images.githubusercontent.com/79809962/148679028-98e41fce-fe47-40d5-b833-9d615c923592.jpg)|![DSC2407](https://user-images.githubusercontent.com/79809962/148679039-b93381e4-b30d-47a6-935f-a1ab66642e18.jpg)|

---

### Resistors

#### Solder the 1k resistors to the back (R7, R8, R9, R10, R11, R12, R19, R20)
![_DSC2362 5](https://user-images.githubusercontent.com/79809962/150558359-0099aee5-0d3a-49af-a78c-c10f4b6cd9de.jpg)

---

#### Solder the 4.7k resistors to the back (R13, R14, R15, R16, R17, R18)
![_DSC2362](https://user-images.githubusercontent.com/79809962/148646613-c9404b94-883f-4991-a0bb-5fea3bde99bc.jpg)

---

### Small Capacitors

#### Solder the 100nF capacitors to the back (C7, C8). If your board has a polarity marking, ignore it unless you are deliberately using larger polarised capacitors than the BOM calls for, in which case make sure they line up with the PCB marking
![_DSC2363](https://user-images.githubusercontent.com/79809962/148646621-f21b893c-dd15-405c-a6d9-2fb33511e9b1.jpg)

---

### Headers

#### Push the male headers into the female headers that you soldered to the Pico PCB
![_DSC2364](https://user-images.githubusercontent.com/79809962/148646627-19794a01-882f-49be-97cc-3787d9a7fa48.jpg)


#### Push the Jack PCB onto the other side of the male headers
![_DSC2365](https://user-images.githubusercontent.com/79809962/148646646-6749c630-28f0-4a59-b08b-adc0be3b2396.jpg)


#### Solder the male headers to the Jack PCB
![_DSC2366](https://user-images.githubusercontent.com/79809962/148646657-fa913959-3f8a-4eac-a3d1-008e663350ac.jpg)


#### Pull the two PCBs apart carefully to reveal the perfectly aligned male headers on the Jack PCB
![_DSC2367](https://user-images.githubusercontent.com/79809962/148646661-d65a2f9f-1f91-484d-80ef-8ee319715e32.jpg)

---

#### OLED Configuration
There are two pin configurations that the OLED used in this build commonly comes in, which are labelled on the board 'TPH' (The Pi Hut), and 'CPC' (CPC, AliExpress, most other suppliers).  
The Pi Hut display is preferable as it does not have pre-soldered headers, so is easier to mount on the board. However the CPC display is still entirely usable.  
  
This configuration setup allows you to tell the module which display you are using, as their pins are ordered differently:  
TPH: VCC, GND, SDA, SCL  
CPC: SDA, SCL, VCC, GND
  
Don't ask my why there is still not a standard for I²C pin layout in the year 2021, but here we are, and here is how to tell the module which layout you are using:
  
#### Snip some resistor legs and bend them over the end of something small and round, such as needle-nose pliers
![_DSC2410](https://user-images.githubusercontent.com/79809962/148679661-a7d45646-1bf8-4c26-bbe6-112b9564b67d.jpg)

#### Push the snipped legs into the holes on the PCB according to the diagram and which OLED you have, and then solder either from the top or the bottom
![_DSC2411](https://user-images.githubusercontent.com/79809962/148679680-a0af5587-3b4e-4cbe-b6a3-b62f499322e1.jpg)


---

### Front Panel Components

#### Solder the push buttons to the front (SW1, SW2)
![_DSC2370](https://user-images.githubusercontent.com/79809962/148646683-57dd2f33-b97a-42d6-8ca1-f99a6ae1e458.jpg)


#### Solder the OLED Display to the front
This is quite an awkward operation as the distance the headers need to occupy is not standard to the lengths that 2.54mm headers come in. If you are using a CPC display, your headers are probably pre-soldered, in which case you need to prop the display up somehow while you solder one pin, then go on to solder the rest once you're sure it's straight.
  
If your display is CPC, the pins will be flush with the PCB if it's at the correct height, which is difficult but possible to solder.  
  
If your display is TPH, you can either solder pins and do it the same way as the CPC method, or use extra-long pin headers instead which will make the soldering process easier, as they will protrude far enough to get a better solder joint.

![_DSC2375](https://user-images.githubusercontent.com/79809962/148646695-8a2f9e91-3963-4d17-b010-45cf7d577ef7.jpg)


#### Place the potentiometers (VR1, VR2) onto the front but don't solder yet
![_DSC2376](https://user-images.githubusercontent.com/79809962/148646698-62511e03-8c8f-488a-865c-0d5167d30f9c.jpg)


#### Place the jacks (J1, J2, J3, J4, J5, J6, J7, J8) onto the front but don't solder yet
![_DSC2377](https://user-images.githubusercontent.com/79809962/148646702-c5d8f407-9fff-4ab2-b7b6-8b6b8a311be6.jpg)


#### Place the LEDs (LED1, LED2, LED3, LED4, LED5, LED6) onto the front but don't solder yet, lining up the short leg with the white stripe on the PCB
![_DSC2378](https://user-images.githubusercontent.com/79809962/148646705-0101c195-e40d-4c73-ba11-2a2696f947ab.jpg)


#### Push the front panel onto the components, lining up the LEDs so they are flush
![_DSC2379](https://user-images.githubusercontent.com/79809962/148646710-56cbc9e0-8c64-49c2-925b-ffeebbacfc23.jpg)


#### Place an elastic band or hair bobble around the PCB and panel to hold them together. I used the plastic coated wire that came with my USB cable
![_DSC2380](https://user-images.githubusercontent.com/79809962/148646763-126851a4-d95e-4cbb-acee-2999e97939d9.jpg)


#### Solder all the components from the back. For the potentiometers, only solder the large lugs on the sides if yours are trimmer type potentiometers. Do not solder the lugs if the potentiometers came with nuts.
![_DSC2381](https://user-images.githubusercontent.com/79809962/148646777-39ab2a58-f383-4861-91d3-d843b07f3ccf.jpg)

---

## Finish off the assembly

#### Screw the PCB standoff onto the Jack PCB so that the standoff is on the back and the screw on the front
![_DSC2383](https://user-images.githubusercontent.com/79809962/148646782-77b899c9-897c-443a-8b71-5c08737046eb.jpg)


#### Push the two PCBs together, keeping them both straight to avoid bending the header pins
![_DSC2384](https://user-images.githubusercontent.com/79809962/148646783-8885266b-4b37-4a82-8a87-bb5049cf1d28.jpg)


#### Screw the second screw into the PCB standoff through front of the Pico PCB to hold the two PCBs together firmly
Don't over-tighten so hard that you damage the PCB, but you also don't want this to rattle loose so make sure it is secure.
![_DSC2385](https://user-images.githubusercontent.com/79809962/148646786-cb37fbc2-1b4d-4ca0-8bff-d7bcea3437dd.jpg)


#### Push the Pico into its slot on the Pico PCB
![_DSC2387](https://user-images.githubusercontent.com/79809962/148646789-12cde45d-cf69-4b90-b8ec-1d442f3778b8.jpg)


#### If not done already, peel the protective film off the OLED display
![_DSC2389](https://user-images.githubusercontent.com/79809962/148646795-981506b6-4cf5-4c02-a21a-cf87ed0cefc4.jpg)


#### Screw all of the nuts on to hold the components to the front panel. 
If your potentiometer came with nuts, use them, otherwise just screw on the jacks.
Also pop on the knobs.
![_DSC2390](https://user-images.githubusercontent.com/79809962/148646798-515a2e9f-a8b3-4853-904e-e0e3da5470fc.jpg)


#### Finally, pop the TL074 and MCP6002 Op-Amps into their respective sockets, making sure the notch in the IC matches the notch on the socket
![_DSC2391](https://user-images.githubusercontent.com/79809962/148646800-d8514481-a453-4ed8-a9d0-edd9f09f9432.jpg)

---

### (Optional) Multimeter Tests
Use your multimeter set to continuity mode for these tests.

#### Check that there is no continuity between +12V and -12V, between +12V and Ground, and between -12V and Ground on the power header
![_DSC2395](https://user-images.githubusercontent.com/79809962/148646810-db50ddd0-6111-429a-9aa6-ef6c4c8132ca.jpg)

If there is continuity on any checks where there shouldn't be then make sure your solder joints are good and that there is no dirt or stray solder bridging any connections. Also make sure that your diodes and power cable are all the correct orientation.

---

### Smoke Test

#### Connect your module to your Eurorack power supply without any other modules connected
![_DSC2396](https://user-images.githubusercontent.com/79809962/148646814-3383e7d1-eda9-4995-a31d-01db47aaaa4e.jpg)

Make sure the cable is connected so that the 'key' on the cable slots into the notch on the header, and the red stripe is on the bottom side of the module.
Turn on your power supply and check for any smoke or discolouration of the PCB around the power connector, and immediately unplug if either occur.  
If all is groovy, the congratulations, you've finished building your EuroPi!

---

## Admire your handiwork!

![_DSC2397](https://user-images.githubusercontent.com/79809962/148646815-992b8188-18b9-4bbd-be4d-92985837d789.jpg)

#### If you have any issues with the build process or programming that are not covered in the [troubleshooting guide](/troubleshooting.md) then please drop us an email at [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.com)

#### Share photos of your build with us on [Instagram](https://www.instagram.com/allensynthesis/), or [email us](mailto:contact@allensynthesis.com)!

#### Now just follow the [programming instructions](/software/programming_instructions.md) to get ready to use your new EuroPi!
