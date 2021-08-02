import os
from config import CONFIG   # configuration scheme
from system import SYS      # current system hardware states and modes

# check processor type to determine if emulator or RPi
if os.uname().machine == "x86_64":
    # simulate rpi gpio
    print("Detected X86 based processor, emulating GPIO")
    from rpisim import GPIO
    # making sure out is the same as in RPi.GPIO for compatibility
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
    SYS["Pressure"]["TANKS_PRESSURIZED"] = True

def depress_propellant_tanks():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_HE_ENTRY"], 1)
    SYS["Pressure"]["TANKS_PRESSURIZED"] = False

def lox_vent_on():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_LOX_VENT"], 0)
    SYS["Pressure"]["LOX_VENT_OPEN"] = True

def lox_vent_off():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_LOX_VENT"], 1)
    SYS["Pressure"]["LOX_VENT_OPEN"] = False

def kero_vent_on():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_KERO_VENT"], 0)
    SYS["Pressure"]["KERO_VENT_OPEN"] = True

def kero_vent_off():
    global SYS, HardwareConfig
    GPIO.output(HardwareConfig["Solenoid_KERO_VENT"], 1)
    SYS["Pressure"]["KERO_VENT_OPEN"] = False

def lox_entry_close():
    GPIO.output(HardwareConfig["Solenoid_LOX_ENTRY"], 1)
    SYS["Ignition"]["LOX_ENTRY_OPEN"] = False

def kero_entry_close():
    GPIO.output(HardwareConfig["Solenoid_KERO_ENTRY"], 1)
    SYS["Ignition"]["KERO_ENTRY_OPEN"] = False

def lox_entry_open():
    GPIO.output(HardwareConfig["Solenoid_LOX_ENTRY"], 0)
    SYS["Ignition"]["LOX_ENTRY_OPEN"] = True

def kero_entry_open():
    GPIO.output(HardwareConfig["Solenoid_KERO_ENTRY"], 0)
    SYS["Ignition"]["KERO_ENTRY_OPEN"] = True

from time import sleep
def ignition():
    global SYS, HardwareConfig
    SYS["Ignition"]["IGNITION_STARTED"] = True
    def deploy_propellant():
        print("deploying propellants")
        lox_entry_open()
        kero_entry_open()

    for _ in range(10):
        sleep(1)
    GPIO.output(HardwareConfig["SIGNAL_IGNITION"], 1)
    sleep(1)
    deploy_propellant()

    print("Here comes the fireworks")
    

    

