# Enhanced Fan Control
Enhanced fan control for the Raspberry Pi that is quiet and more efficient - works on both Raspbian and Ubuntu.

Instead of simple bang-bang control that is included in the latest Raspberry Pi OS, this script provides linear proportional control with sinking. That means the fan stays quiet and the device stays cooler while reducing power consumption used by the fan.

To use, you need Python 3.7+ and to install the  `gpiozero` library: `pip3 install gpiozero`

It can be run with `python3 fan.py` or added to systemd to start on boot.

## Ubuntu Support
Make sure the user running this script is part of the `dialout` group (required for GPIO access). You will also need to install `gpiozero` and `RPi.GPIO`:

```bash
sudo usermod -aG dialout $(whoami) # Add to dialout group
export LC_ALL=C  # Required for RPi.GPIO to build correctly
export CFLAGS=-fcommon  # Required for RPi.GPIO to build correctly
pip3 install --upgrade gpiozero RPi.GPIO
logout # To apply the usergroup changes (reloading doesn't seem to work)
```
