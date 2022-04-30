# EuroPi Error Codes

These are error codes that can be used by any script, although are primarily for use within the firmware when certain anomalies are detected.

| Error Code  | Description | Solution |
| ----------- | ----------- | ---------|
| 1           | Calibration did not complete properly       | Attempt calibration again, ensuring rack power is on |
| 2           | OLED display not detected        | Ensure the OLED is soldered correctly, and that the OLED configuration headers are oriented correctly according to the pinout of your specific display |
| 3           | Provided text exceeds the display size | Reduce the text being displayed, or display it sequentially or using the .scroll() feature |