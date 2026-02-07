# EuroPi (surface-mount) Build guide
If you want to build this version of the EuroPi, you can buy the PCB directly from [Allen Synthesis](https://allensynthesis.square.site/product/europi-panel-pcb/16?cp=true&sa=true&sbp=false&q=false), and the remaining parts from the sources listed in the [bill of materials](/hardware/surface-mount/bill_of_materials.md)
1. Press fit the Thonkiconn audio jacks (x8), 9mm Potentiometers (x2), Buttons (x2), and LEDs (x6) to the PCB, but don't solder anything yet.

    ![IMG_4543](https://github.com/user-attachments/assets/6196178e-a7c9-4535-b5e5-85d95e728b74)
1. Put the panel on and just use an elastic band to hold it in place, making sure all the components fit through their cutouts properly.

    ![IMG_4544](https://github.com/user-attachments/assets/a3283c42-c10b-4cab-80d6-dbe6f63b6ec0)
1. Solder the jacks and potentiometers from the back, making sure they're properly aligned with the panel and not at a funny angle.
1. Now solder the buttons, taking care to make sure they're pushed against the PCB while doing so - they might try to fall out so it can help to just solder one pin first and keep the solder hot with your iron while you position it, and only solder the other 3 pins once you're happy.
1. To solder the LEDs, use the one pin trick again: solder just one pin of each LED and then push the LED flush with the panel with one hand while using the other to hold the soldering iron, keeping that pins solder molten.
1. Finally solder the remaining pins of each LED (and the buttons if you only soldered one pin of each of those)

    ![IMG_4546](https://github.com/user-attachments/assets/fcc6625f-eacf-44f8-8927-24b103c9de45)
1. Snip off the long LED legs using wire snips or the cutting part of a pair of pliers.
1. Solder the male headers (x2) onto the Raspberry Pi Pico (skip this step if you're using a Pico H which has them pre-soldered). I find that a breadboard is a useful tool to make sure the pins are completely straight.

    ![IMG_4555](https://github.com/user-attachments/assets/e15e92af-1980-47af-9f75-a4929c9caa9d)
1. Push the female headers (x2) onto the male headers, and then push both onto the back of the PCB.

    ![IMG_4558](https://github.com/user-attachments/assets/a8cc92df-6143-4f91-af92-e481dbdcda11)
1. Turn the PCB over and solder all of the Pico pins on both sides, making sure the Pico stays straight. Again it can help to just solder one pin at each end of each header, make sure its straight and re-heat the solder if necessary, and then continue soldering all the other pins only once you're happy.

    ![IMG_4559](https://github.com/user-attachments/assets/e1b446ef-06ca-4110-b85e-780f75c1d94b)
1. Now it's time to solder the OLED, which is easily the most difficult part of this build. You need to apply a small amount of solder to each of the pins while holding the OLED in place with your other hand, so it can help to use some kind of desk clamp. Run the soldering iron over each of the 4 pins quickly enough that the solder on all of them stays molten, and use your other hand to make sure the display is straight while the solder cools. The pins should only just be flush with the back of the PCB, so I find it easier to solder from the top (but make sure none of the pins are bridged together).

    ![IMG_4560](https://github.com/user-attachments/assets/07483aa2-d90e-465d-aa1f-b427b1db0e30)
1. Solder the Eurorack power header and (optional) I2C header by fitting them and turning the board over to solder from the other side. If they're a bit loose you might need to use an elastic band to hold them in place while you solder one pin, then remove and solder the rest.

    ![IMG_4564](https://github.com/user-attachments/assets/11308b06-3f1b-49c0-9650-565ddf0fca48)
1. Follow the [programming instructions](/software/programming_instructions.md) to set the module up for however you want to use it, calibrate it if you want higher accuracy, and have fun!

    ![IMG_4566](https://github.com/user-attachments/assets/aed31128-227d-4bcb-9529-86b588602962)

