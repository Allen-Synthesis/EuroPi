# EuroPi Error Codes

These codes will be displayed both in the console (if connected to a computer) and on the OLED display for 5 seconds when raised.
They are meant to provide an alternative to halting a script if a predictable error occurs, for example the OLED not being detected by the hardware.
They can be used in custom scripts, however it would be mroe sensible to simply avoid a situation where they would be required, and if that situation does arise, it is more likely that a pull request to add that error to the firmware europi.py would be the correct course of action!

| Error Code | Meaning | Solution |
| ---------- | ------- | -------- |
