# Sequencer

author: Rory Allen (github.com/roryjamesallen)

date: 21/08/2023

labels: sequencer, triggers

## What can it do?
The script gives you two identical sequencers which can be independently set up, but share a clock which must be externally supplied via the digital input.  
Each sequence can be 1-32 steps long, and each step can be any note from C0 to B4, or off. When set to any note value other than off, the trigger output for the sequence will remain on for as long as the external clock does for that note. If the note is set to off, the trigger output will not turn on.  
In the default view, you can see both sequences with the height of each bar representing the note pitch, and a thin line indicating the current position of each sequence.  
As the sequences can have different lengths, the indicator for each sequence can show differently, which can help to keep track of the sync between the sequences, and help to visualise polyrhythms between them.

The menu structure which allows the settings to be edited is arranged like this:
```
0| EDIT SEQUENCE - K2 selects the new sequence to be edited
    1|---- Step X - K2 selects the step from the selected sequence
        2|---- EDIT LENGTH - K2 selects the new length for the selected sequence
        3|---- Step X - Note - K2 selects the new note for the selected step
```
- Menu level 1 is the default menu level, and pressing B2 while in either menu level 2 or 3 will confirm the new value set (either length or note) and return to menu level 1.
- At any level of the menu other than 0, long pressing B2 will move to menu level 0 *without* saving the currently highlighted value, so if you click on a step to edit and then decide not to, you can exit without risking changing it.  
- At menu level 1, you can select any step of the sequence by highlighting it with K2 and then pressing B2, or use K2 to scroll all the way to the left then press B2 to edit the length of the sequence.  
- When editing the sequence length, the indicator shows how long the sequence will be if B2 is pressed to confirm the new length.

# Controls
- digital_in: Clock in
- analog_in: n/a
- knob_1: n/a
- knob_2: Menu navigation
- button_1: n/a
- button_2:  
  Short Press: Select  
  Long Press: Change sequence to edit
- output_1: Sequence 1 Trigger
- output_2: Sequence 1 1V/Oct
- output_3: n/a
- output_4: Sequence 2 Trigger
- output_5: Sequence 2 1V/Oct
- output_6: n/a
