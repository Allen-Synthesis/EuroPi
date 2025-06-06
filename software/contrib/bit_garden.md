# Bit Garden - pseudo-random deterministic repeated triggers

Connect a trigger or gate source to the Digital input and the each output will
mirror that signal according to a decreasing deterministic probability pattern
set by the seed value. Use the Analog input as a trigger to get a new random
seed. From the main page, use the left knob adjust the pattern length. The
right knob will scroll through each output to show the current trigger pattern
for that output. Left button will change the cv output mode from Trigger
(mirror the digital input), Gate (100% duty cycle of trigger input), or Flip
(toggle the cv on/off upon each digital input according to the pattern). Hold
the left button to edit each output's probability, and hold the right button
to manually change the seed value.

## User Interface

```yaml
Main Page:
  K1: Sequence Length
  K2: Scroll through output pattern display
  B1:
    Short Press - Change cv output mode
    Long Press - Enter probability edit mode
  B2:
    Short Press - Randomize seed
    Long Press - Enter seed edit mode

Probability Edit Page:
  K1: [unused]
  K2: Adjust probability of selected cv
  B1:
    Short Press - Change cv output
    Long Press - [unused]
  B2:
    Short Press - Return to main page
    Long Press - [unused]

Seed Edit Page:
  K1: [unused]
  K2: Scroll through hex value for current digit
  B1:
    Short Press - Change seed digit position
    Long Press - [unused]
  B2:
    Short Press - Return to main page
    Long Press - [unused]
```

## Basic Usage

1. Connect a clock input to the Digital input
2. Triggers will appear on the outputs.
3. Adjust the pattern length using K1.
4. Press B2 to find a pattern you like.

## Patch Tips

Patching Drums:

- Use a medium probability for a kick drum
- Use a low probability for snare
- Use a high probability for hi-hats
- Use a low probability for open hi-hat or other drum accent

Using Bit Garden as a melodic sequencer:

- Connect 3+ output to a cv mixer
- Adjust each input to varrious levels
- Send the sum into a quantizer
- Press B2 to reseed for a new sequence

Slow clock with Flip mode

- Connect a slow clock to Digital input
- Press B1 until Flip mode is selected
- Use slow changing output as gates for turning patch features on/off
