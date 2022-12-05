# Change Log

### 2022-08-28

- [Release] version 0.6.1
- [Bug Fix] Add new `experimental` package to firmware setup.py (https://github.com/Allen-Synthesis/EuroPi/issues/164)

### 2022-08-28

- [Release] version 0.6.0
- [New Script] Turing Machine  (https://github.com/Allen-Synthesis/EuroPi/pull/114)
- [New Script] Smooth random voltages  (https://github.com/Allen-Synthesis/EuroPi/pull/153)
- [New Script] Probapoly - polyrhythmic gate patterns  (https://github.com/Allen-Synthesis/EuroPi/pull/161)
- [Bug Fix] Consequencer - Added probability-based steps in patterns  (https://github.com/Allen-Synthesis/EuroPi/pull/158)
- [Bug Fix] Consequencer - Increased reset_timeout to allow for slower BPMs  (https://github.com/Allen-Synthesis/EuroPi/pull/158)
- [Bug Fix] Strange Attractor - init save state  (https://github.com/Allen-Synthesis/EuroPi/pull/157)
- [Bug Fix] CVecorder - Updated loading screen to show progress to avoid a perception of a hang during load  (https://github.com/Allen-Synthesis/EuroPi/pull/161)
- [Bug Fix] CVecorder - Reduced number of save-state loading retries for faster loading  (https://github.com/Allen-Synthesis/EuroPi/pull/161)
- [Bug Fix] CVecorder - Fixed bug that caused recordings to be buggy if no save state file was found  (https://github.com/Allen-Synthesis/EuroPi/pull/161)
- [API] New experimental package added including `LockableKnob` and `KnobBank`  (https://github.com/Allen-Synthesis/EuroPi/pull/155)
- [Other] Add .vscode to gitignore to ignore user IDE settings

### 2022-05-24

- [Release] version 0.5.0
- [New Script] PolySquare 6 oscillator contrib script https://github.com/Allen-Synthesis/EuroPi/pull/141
- [Bug Fix] Updated display to show pattern number, decrease loading times #146
- [Bug Fix] Cvecorder bank clear remediation #139,
- [Documentation] Contributing updates #138, #125
- [Documentation] Update hamlet.md to align gate/CV ports with code #135
- [Other] Add a new test fixture called MockHardware #137
- [Other] Add missing test mocks #143

### 2022-04-28

- [Release] version 0.4.0
- [New Script] Hamlet, mod to Consequencer adding two voice tracks #129
- [New Script] Bernoulli gates, dual Bernoulli gates #104
- [New Script] CVecorder, record cv sequences #121
- [Bug Fix] coin_toss triggering on falling slope instead of rise #117
- [Bug Fix] remove for loop that was calling _set_duty() multiple times #126
- [Bug Fix] Poly-rhythmic Seq sequence reset #130
- [Other] add a test for menu's imports #120
- [Other] Harmonic LFOs updates #127, #128


### 2022-04-13

- Consequencer: Moved self.reset_timeout = 500 to a better place
- Consequencer: Reduced latency by removing the if self.clock_step < 128 check
- Consequencer: You can now add patterns longer than 32 steps without breaking anything 🙂
- Consequencer: Added new patterns inspired by African beats and one based on the Fibonacci sequence
- Consequencer: Added a feature to send a clock out of output 4 which is always in time with the Consequencer. I found this useful to combat the latency between the clock sent to the Consequencer and the gates that come out. With self.output4isClock set to True you can clock all your other modules using output 4 and they will be in-sync with the Consequencer
- Consequencer: Added explanation of self.output4isClock to doc
- Consequencer: Added UI access to self.output4isClock (long-press of button 1)
- CVecorder: Added

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