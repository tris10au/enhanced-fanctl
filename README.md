# Enhanced Fan Control
Enhanced fan control for the Raspberry Pi that is quiet and more efficient

Instead of simple bang-bang control that is included in the latest Raspberry Pi OS, this script provides linear proportional control with sinking. That means the fan stays quiet and the device stays cooler while reduicing power consumption used by the fan.

To use, you need Python 3.7+ and to install the  `gpiozero` library: `pip3 install gpiozero`

It can be run with `python3 fan.py` or added to systemd to start on boot.
