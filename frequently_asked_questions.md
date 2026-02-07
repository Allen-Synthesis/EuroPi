# FAQ

### Frequently asked questions about the EuroPi project. If you can't find the answer to your question here, head over to [The Discord](https://discord.gg/JaQwtCnBV5) and ask it in the support channel!

#

### Topics:

### [General Questions](#general-questions)
### [Hardware Decisions](#hardware-decisions)
### [Bill of Materials (BOM)](#bill-of-materials)
### [Git](#git)
### [Programming](#programming-1)
### [Calibration](#calibration-1)

#

## General Questions

| Can the EuroPi process audio? | Some audio has been achieved on the EuroPi, such as t-schreibs' [Poly Square](software/contrib/poly_square.md) script, however full audio processing would likely require extra hardware to be accurate |
|--|--|

## Hardware Decisions

| Why did you use potentiometers and not encoders? | This module is designed to be a platform with which you can design fully functioning modules of your own, rather than a deep menu based system, and I feel that using encoders would encourage user interfaces that stray into the unusable. Users can always add encoders using i²c if they're determined! |
|--|--|

## Bill of Materials

| Do any of the capacitors need to be polarised? | No, non-polarised will work fine |
|--|--|

## Git/GitHub

| What is a 'Pull Request'? | This is a request made by a user to the main repository to 'pull' the extra data, either changes, new files, or deletions, from their fork into the main one. Essentially it is the way that users contribute to the main repository. The guidelines for creating a PR, and more explanation of what one is, can be found in the [contributing guidelines](contributing.md) |
|--|--|

## Programming

| Do I need to learn programming to use this module? | Nope! The menu system can be used with absolutely no programming knowledge at all, but once installed you are always free to write your own scripts if you feel like it |
|--|--|

## Calibration

| When in the second stage of calibration, my module never reaches 10V, what do I do? | Refer to the [troubleshooting guide](troubleshooting.md) |
|--|--|
