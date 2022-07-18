# Programming Limitations

As with all hardware, the EuroPi has certain limitations set by the hardware. Some are more obvious and are required knowledge for any user, and some are more in depth and are only relevant if you will be programming the module yourself.

### Obvious Limitations
- Analogue input is only 0-10V
- Digital input can only detect signals above 0.7V (meaning it may trigger accidentally if you have a noisy 'low' state)
- Outputs, analogue input, and knobs, have a maximum resolution of 12 bits (4096 steps)
- Debouncing of the buttons means that very fast double presses may not be detected

### Programming Limitations
- Clock pulses shorter than approximately 0.01s will not be reliably detected (this depends on clock speed too)
- Reading any analogue source, either the analogue input or knobs, will result in a slight delay of the script (this can be reduced by using fewer samples, at the cost of accuracy)
