# Change Log

### 2022-04-13

- Consequencer: Moved self.reset_timeout = 500 to a better place
- Consequencer: Reduced latency by removing the if self.clock_step < 128 check
- Consequencer: You can now add patterns longer than 32 steps without breaking anything 🙂
- Consequencer: Added new patterns inspired by African beats and one based on the Fibonacci sequence
- Consequencer: Added a feature to send a clock out of output 4 which is always in time with the Consequencer. I found this useful to combat the latency between the clock sent to the Consequencer and the gates that come out. With self.output4isClock set to True you can clock all your other modules using output 4 and they will be in-sync with the Consequencer
- Consequencer: Added explanation of self.output4isClock to doc
- CVecorder: Added comments to unused functions which are reserved for future use
- Cvecorder: doc updates
- Cvecorder: Added menu handling code

### 2022-04-04

- release version 0.3.0
- add save/load script state behavior via EuroPiScript
- add Strange Attractor chaotic modulation script
- add Noddy Holder sample/track and hold script

### 2022-03-16

- release version 0.2.0

### 2022-03-16

- add bootloader menu allowing the user to choose a script to run
- update all existing scripts to work with the menu
- add new firmware module 'europi_script' containing a base class to support menu inclusion
- add new firmware module 'ui' as a place to hold reusable UI components

### 2022-03-10

- release version 0.1.0

### 2022-02-18

- update diagnostic script to add temperature display and CV output rotation.

### 2022-02-15

- add Consequencer script

### 2022-02-04

- Add support for automated testing
- Add scope script

### 2022-02-01

- added {meth}`europi.DigitalReader.handler_falling()` To define a callback function to call when a falling edge is detected

### 2021-10-15 - 2022-02-02

- initial development of EuroPi library and documentation, including the following scripts:
  - calibrate
  - coin_toss
  - diagnostic
  - harmonic_lfos
  - polyrhythmic_sequencer
  - radio_scanner