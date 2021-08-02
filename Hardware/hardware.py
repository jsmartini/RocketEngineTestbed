import os
from config import CONFIG   # configuration scheme
from system import SYS      # current system hardware states and modes

# check processor type to determine if emulator or RPi
if os.uname().machine == "x86_64":
    # simulate rpi gpio
    print("Detected X86 based processor, emulating GPIO")
    from rpisim import GPIO
    GPIO.OUT = GPIO.MODE_OUT
else:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

print("Initializing GPIO")

global HardwareConfig
HardwareConfig = CONFIG["HardwareConfig"]

for k in HardwareConfig.keys():
    if "Solenoid" in k:
        # solenoids are not acuated on high signal
        GPIO.setup(HardwareConfig[k], GPIO.OUT)
        GPIO.output(HardwareConfig[k], 1)
    else:
        # ignition
        GPIO.setup(HardwareConfig[k], GPIO.OUT)
        GPIO.output(HardwareConfig[k], 0)

def reset_gpio():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

def press_propellant_tanks():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_HE_ENTRY"], 0)
    SYS["TANKS_PRESSURIZED"] = True

def depress_propellant_tanks():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_HE_ENTRY"], 1)
    SYS["TANKS_PRESSURIZED"] = False

def lox_vent_on():
    global SYS, HardwareConfig

def lox_vent_off():
    global SYS, HardwareConfig

def kero_vent_on():
    global SYS, HardwareConfig

def kero_vent_off():
    global SYS, HardwareConfig

def ignition():
    global SYS, HardwareConfig

