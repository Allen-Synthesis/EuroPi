# Set Timer

Set Timer is a simple manual or CV controlled clock/stopwatch to help track how long you've been
playing or recording.

## Inputs & Outputs

- `din`: Start/stop input. See configuration, below
- `ain`: Split trigger.
- `b1`: Start/stop button
- `b2`: Split/reset button. Will reset when stopped, or start a new split timer when running.
- `k1-6`: Unused
- `cv1`: High when the timer is running, low when stopped
- `cv2`: Outputs a 10ms trigger every time a new split timer starts
- `cv3-6`: Unused

## Configuration

The operating mode of the CV input to the timer can be set by creating/editing
`config/SetTimer.json`:
```json
{
    "MODE": "gate"
}
```
The `MODE` field can be set to either `gate` (default) or `trigger`:
- `gate`: The timer starts on the rising edge of the input signal and stops on the falling edge.
- `trigger`: The timer responds to the rising edge of the input signal and will toggle between
  starting or stopping.

## Patching Suggestions

Connect our master clock's on/off output to `din` to start/stop the clock automatically. Connect
the trigger output on `cv2` to a sequencer or switch to coordinate changes at the same time you
start a new split.
