# Probapoly - A polyrhythmic gate generator with probabilty

Probapoly creates interesting polyrhythmic gate patterns while also allowing probabilities to be set
on gates. Given values for and upper and lower rhythmic ratios, Probapoly will create a looping
pattern as short as possible with no repetition of the pattern within the loop.

Outputs 1,2 and 3 output gates based on the upper rhythmic ratio. Outputs 4,5 and 6 output gates
based on the lower rhythmic ratio.

Outputs 1 and 4 always have a probability of 100%. Outputs 2 and 5 have a default probability of
50%. Outputs 3 and 6 have a default probability of 25%.

- digital_in: Clock input
- analog_in: Different mode, adjusted by setting self.ainMode as follows:
    - Mode 1: Analogue input toggles double time feature
    - Mode 2: Analogue input voltage adjusts the upper poly value
    - [default] Mode 3: Analogue input voltage adjusts the probabilities of outputs 2,3,5,6 sending
      gates

- button_1:
    - Short press (<500ms): Reduce pattern length (using manual pattern length is ON).
    - Long Press (>500ms): Toggle doubletime feature
- button_2:
    - Short press (<500ms): Reduce pattern length (using manual pattern length is ON).
    - Long Press (>500ms): Toggle Manual pattern length feature

- knob_1: Select upper polyrhythm value
- knob_2: Select lower polyrhythm value

- output_1: Gate upper polyrhythm
- output_2: Gate upper polyrhythm (50% probability)
- output_3: Gate upper polyrhythm (25% probability)
- output_4: Gate lower polyrhythm
- output_5: Gate lower polyrhythm (50% probability)
- output_6: Gate lower polyrhythm (50% probability)

## Demo video

https://www.youtube.com/watch?v=Rflmr2yJYG0

## Display

Top Row: Upper ratio value, output 2 probability, output 3 probability
Bottom Row: Lower ratio value, output 5 probability, output 6 probability

Top right: current step / pattern length

## Getting Started

The following sections provide instructions for using Probapoly to create some interesting rhythms.

### Initial Connections

1. Connect a 50% duty cycle gate / clock to the Digital input
2. (Optional) Connect a CV source to the analogue input (0 to +5V works best)
3. Connect each output (1 to 6) to modules you want to send gates to

### Creating Polyrhythms

1. Use knob 1 to set the upper ratio and knob 2 to set the lower ratio. Changing these values will
   cause Probapoly to update the gate patterns in real-time.

The value of the upper and lower values determine the frequency of a gate output based on the
incoming clock. A value of 1 will output a gate every 1 clock trigger, a value of 3 will output a
gate every 3 clock triggers.

Outputs 1,2 and 3 use the same rhythm, but with probabilities of 100, 50 and 25% respectively.
Outputs 4,5 and 6 use the same rhythm, but with probabilities of 100, 50 and 25% respectively.

See below for some examples.

#### 1:$ Four to the floor
upper: 1
lower: 4
automatically calculated pattern length: 4

#### 2:3 Hemiola
upper: 2
lower: 3
automatically calculated pattern length: 6

#### 4:3 Four over Three (Pass the god damn butter)
upper: 4
lower: 3
automatically calculated pattern length: 12

#### 16:15
upper: 16
lower: 15
automatically calculated pattern length: 240

## Example patches

### Polyrhythmic percussion with probabilistic decay and FX movement

This patch will create a polyrhythm with two percussive elements. On 50% of the gates, the kick and
tom decay will be changed. On 25% of the gates an FX module will have it's parameters tweaked.

- Connect output 1 to some percussion element (e.g. a kick)
- Connect output 2 to an envelope, connect the envelope to the kick decay
- Connect output 3 to an envelope, connect the envelop to wet/dry CV input on an FX module

- Connect output 4 to some percussion element (e.g. a tom)
- Connect output 5 to an envelope, connect the envelope to the tom decay
- Connect output 6 to an envelope, connect the envelop to another CV input on an FX module

- Set the upper value to 4
- Set the lower value to 3

### Polyrhythmic melodies

This patch uses the polyrythmic gates to advance sequencer clocks

- Connect output 1 to the clock input of sequencer 1
- Connect output 4 to the clock input of sequencer 2

- Create a short (e.g. 4) pattern on both sequencers

- Adjust the upper and lower values manually or during a performance to created interesting and
  fluid polyrhythmic melodies
