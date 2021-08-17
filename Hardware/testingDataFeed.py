import zmq
import asyncio
import pickle
import json
from util import TS

from math import sin
from random import random

def loadcell_data_generator():
    yield {
        "NODE_NAME": "Dummy Load CELL",
        "SENSOR_NAME": "Dummy Load CELL #1",
        "VOLTAGE_RATIO": sin(1/random() *random()),
        "TIME": TS()
    }

def pressure_data_generator():

    def scaleNSmooth_dummy():
        return {
            "LOX_PSI": random(),
            "KERO_PSI": random()
        }

    yield {
        "LOX_PSI": random(),
        "KERO_PSI": random(),
        "TIME": TS()
    }


async def testing_pub(**kwargs):
    
    # copy pasted from other pub implementations
    # loadcellpub.py
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
    try:
        cell_name = kwargs['cell_name']
    except BaseException as e:
        pass
        #set up zmq context
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.PUB)
        #host publisher on localhost @ port
    socket.bind(f"tcp://*:{port}")

    # custom function input for data packet generation
    data_generator = kwargs['data_generator']

    while True:
        data = next(data_generator())
        #print(data)
        socket.send(
                pickle.dumps(
                    json.dumps(
                        data
                    )
                )
            )
        await asyncio.sleep(update_tick)




