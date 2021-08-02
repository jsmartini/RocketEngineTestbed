from dataNode import DataPublisher
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.Manager import *
import asyncio
import zmq
import pickle
import json
from util import TS # time stamp macro as float

async def LoadCellPub(**kwargs):
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
    cell_name = kwargs['cell_name']
        #set up zmq context
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.PUB)
        #host publisher on localhost @ port
    socket.bind(f"tcp://*:{port}")
        
        #holds messages if system can't keep up      
    def onVoltage(self, vr):
        socket.send(
            pickle.dumps(
                json.dumps(
                    {
                        "NODE_NAME"    : node_name,
                        "SENSOR_NAME"  : cell_name,
                        "VOLTAGE_RATIO": vr,
                        "TIME": TS()
                    }
                )
            )
        )
    
    volr = VoltageRatioInput()
    volr.setOnVoltageRatioChangeHandler(onVoltage)
    volr.openWaitForAttachment(5000)

    # work forever
    while True:
        await asyncio.sleep(update_tick)