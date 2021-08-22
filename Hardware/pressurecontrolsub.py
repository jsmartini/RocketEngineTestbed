import zmq
import asyncio
import sys
import os
from util import *
import zmq
from config import *
from system import *
from pressurepub import CURRENT_PRESSURE_READINGS # get readings
from hardware import kero_vent_off, kero_vent_on, lox_vent_on, lox_vent_off

def toggle_pid():
    global SYS
    SYS["PressureControl"]["PID_ON"] = not SYS["PressureControl"]["PID_ON"]
    return SYS["PressureControl"]["PID_ON"]

class PID:

    def __init__(self, **kwargs):
        self.gains = kwargs['gains']
        self.integral = 0
        self.time_step = kwargs['time_step']
        self.last_error = 0
        self.setpoint = 0
        self.name = kwargs["name"]
        if self.name == "KERO":
            self.vent_on = kero_vent_on
            self.vent_off = kero_vent_off
        else:
            self.vent_on = lox_vent_on
            self.vent_off = lox_vent_off

    def new_setpoint(self, new_point):
        self.setpoint = new_point
    
    def update(self, value):
        error = self.setpoint - value
        proportional = self.gains["p"] * error
        derivative = self.gains["d"] * (error - self.last_error) / self.time_step
        self.integral += self.gains["i"] * error * self.time_step
        self.last_error = error
        return proportional + self.integral + derivative

    def __call__(self, value):
        global SYS
        err = self.update(value)
        if err < 0: # value inputted into the system is larger than the set point
            self.vent_on()
        else:
            self.vent_off()    
        return err
        # define venting and error code with windup
        # update system states as well

async def PressureControllerPub(**kwargs):
    global CONFIG
    global SYS

    """
    
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.SUB)
    socket.connect(f"tcp://*:{port}")

    LOXPID = PID(
        gains = CONFIG["LOXPIDGains"],
        time_step = update_tick
    )
    KEROPID = PID(
        gains = CONFIG["KEROPIDGains"],
        time_step = update_tick
    )

    LOXPID.new_setpoint(CONFIG["PressureConfig"]["LOX_MAX_PSI"])
    KEROPID.new_setpoint(CONFIG["PressureConfig"]["KERO_MAX_PSI"])
    """

    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
    port = kwargs['port']
    
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.PUB)
    socket.bind(f"tcp://*:{port}")
    LOXPID = PID(
        gains = CONFIG["LOXPIDGains"],
        time_step = update_tick,
        name = "LOX"
    )
    KEROPID = PID(
        gains = CONFIG["KEROPIDGains"],
        time_step = update_tick,
        name = "KERO"
    )
    LOXPID.new_setpoint(CONFIG["PressureConfig"]["LOX_MAX_PSI"])
    KEROPID.new_setpoint(CONFIG["PressureConfig"]["KERO_MAX_PSI"])

    while True:

        while SYS["PressureControl"]["PID_ON"]:

            socket.send(
                pickle.dumps(
                    json.dumps(
                        {
                            "LOX_ERROR":LOXPID(CURRENT_PRESSURE_READINGS["LOX_PSI"]),
                            "KERO_ERROR":KEROPID(CURRENT_PRESSURE_READINGS["KERO_PSI"])
                        }
                    )
                )
            )
            
            await asyncio.sleep(update_tick)
    
        await asyncio.sleep(update_tick*100)

    





