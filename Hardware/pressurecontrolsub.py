import zmq
import asyncio
import sys
import os
from util import *
import zmq
from config import *
from system import *

class PID:

    def __init__(self, **kwargs):
        self.gains = kwargs['gains']
        self.integral = 0
        self.time_step = kwargs['time_step']
        self.last_error = 0
        self.setpoint = 0

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
        # define venting and error code with windup
        # update system states as well

async def PressureControllerSub(**kwargs):
    global CONFIG
    global SYS
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.SUB)
    socket.connect(f"tcp://127.0.0.1:{port}")

    LOXPID = PID(
        gains = CONFIG.LOXPIDGains,
        time_step = update_tick
    )
    KEROPID = PID(
        gains = CONFIG.KEROPIDGains,
        time_step = update_tick
    )

    LOXPID.new_setpoint(CONFIG.PressureConfig.LOX_MAX_PSI)
    KEROPID.new_setpoint(CONFIG.PressureConfig.KERO_MAX_PSI)

    while True:

        while SYS["PressureControl"]["PID_ON"]:

            data = socket.recv()
            LOXPID(data["DATA"]["LOX_PSI"])
            KEROPID(data["DATA"]["KERO_PSI"])

            await asyncio.sleep(update_tick)
    
        await asyncio.sleep(update_tick*100)

    





