# Noddy Holder

author: Sean Bechhofer (github.com/seanbechhofer)  
date: 2022-03-26
labels: gates, sample&hold, track&hold

*Cum On Feel the Noize!* Two channels of sample/track and hold based on
a single trigger and CV source.

Digital in is a gate, Analog in is arbitrary CV.

Output 1 is the original gate, Output 2 is S&H based on gate and CV,
Ouput 3 is T&H based on gate and CV.

Outputs 4, 5 and 6 are similar, but with the gate *inverted*. 

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis: https://github.com/Allen-Synthesis/EuroPi

# Controls

- digital_in: Gate
- analog_in: CV

- knob_1: 
- knob_2: 

- button_1: 
- button_2: 

- output_1: gate 
- output_2: s&h based on gate
- output_3: t&h based on gate
- output_4: inverted gate
- output_5: s&h based on inverted gate
- output_6: t&h based on inverted gate

## Basic Usage
1. Switch on
2. Connect outputs to modules
3. Send gate and CV to inputs
4. Send resulting gates and CV to modules

## Controls
1. There are no controls. Noddy doesn't listen to The Man.

## Details

*Sample & Hold:* When gate goes ```HIGH```, CV is sampled, and the resulting value is
output until the gate goes ```HIGH``` again and we re-sample.

*Track & Hold:* When gate is ```HIGH```, CV input is mirrored to the
output. When gate goes ```LOW```, CV is sampled and the resulting value is
output until the gate goes ```HIGH``` again. 
