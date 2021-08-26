from gpiozero import PWMOutputDevice
from datetime import datetime, timedelta
import subprocess
import time
import os


CONTROL_PIN = PWMOutputDevice("GPIO14") # Pin to control fan (can be hardware 
                                        # or software-enabled PWM so the 
                                        # specific pin does not matter)

ACTIVATE_TEMP = 58.0 # Tenperature to turn fan on
DEACTIVATE_TEMP = 56.0 # Temperature to turn fan off
MAX_TEMP = 63.0 # Temperature at which fan should be 100%

MIN_POWER = 0.10 # The starting power [0...1]. Most fans require some 
                 # power to overcome static friction
MAX_POWER = 1.00 # The maximum power 


ACTIVATED_FREQ = 10 # (seconds) How frequently to check temperature while fan
                    # is enabled
DEACTIVED_FREQ = 20 # (seconds) How frequently to check when fan is not running

EPSILON = 0.005
LAST_VALUE = None

HAS_VCGENCMD = None


def double_equal(a, b, eps=EPSILON):
    return abs(a - b) <= eps


def calculate_power(temp):
    global ACTIVATE_TEMP, MAX_TEMP, MIN_POWER, MAX_POWER, LAST_VALUE

    if temp < DEACTIVATE_TEMP and LAST_VALUE not in (0, None):
        return 0

    if temp < ACTIVATE_TEMP and LAST_VALUE in (0, None):
        return 0
    elif temp < ACTIVATE_TEMP:
        return LAST_VALUE

    if temp >= MAX_TEMP:
        return 1

    ratio = (temp - ACTIVATE_TEMP) / (MAX_TEMP - ACTIVATE_TEMP)
    return (MAX_POWER - MIN_POWER) * ratio + MIN_POWER


def set_pin(value):
    global CONTROL_PIN, LAST_VALUE

    if LAST_VALUE is not None and double_equal(LAST_VALUE, value, 0.05):
        print("Skipping setting fan as value has not changed")
        return

    if double_equal(0.0, value):
        CONTROL_PIN.off()
        print("Turning fan off")
    else:
        CONTROL_PIN.value = value
        print("Setting fan to", value)

    LAST_VALUE = value


def get_temperature():
    global HAS_VCGENCMD
    
    # Raspbian has `vcgencmd` but Ubuntu does not so uses thermal zone data
    if HAS_VCGENCMD is None:
        result = subprocess.run(["which", "vcgencmd"], capture_output=True)
        HAS_VCGENCMD = (result.returncode == 0)

    if HAS_VCGENCMD:
        cmd = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
        return float(cmd.stdout.decode("utf-8").strip().split("=")[1].split("'")[0])
    else:
        zones = [f for f in os.listdir("/sys/class/thermal/") if f.startswith("thermal_zone")]
        if len(zones) == 0:
            raise Exception("Cannot read temperature - no vcgencmd and no thermal zones")
        with open(os.path.join("/sys/class/thermal", zones[0], "temp"), encoding="utf-8") as f:
            return float(f.read().strip()) / 1000


def adjust_fan():
    temp = get_temperature()
    print("Temperature is", temp)
    power = calculate_power(temp)
    print("Power state is", power)
    set_pin(power)
    return 1 if double_equal(power, 0.0) else 0


def run_task():
    while True:
        start = datetime.now()
        ret = adjust_fan()
        delta = (
            (start + timedelta(seconds=(20 if ret else 10))) - datetime.now()
        ).total_seconds()
        if delta < 1:  # SOmetihg went wrong and processing took > 10 seconds
                       # Typically means system is failing and vcgencmd is not
                       # responding - most common on RPi3 and older
            delta = 10
        print(datetime.now(), "Sleeping for", delta, "\n")
        time.sleep(delta)


if __name__ == "__main__":
    run_task()
