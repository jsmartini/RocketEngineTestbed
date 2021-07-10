import zmq
import asyncio
from util import *
import pickle
import json

global SYS
SYS = {
    "Pressure": {
        "LOX_VENT_OPEN": False,
        "KERO_VENT_OPEN": False,
        "TANKS_PRESSURIZED": False,
    },
    "Ignition": {
        "IGNITION_STARTED": False,
        "KERO_ENTRY_OPEN": False,
        "LOX_ENTRY_OPEN": False,
    }
}


async def SystemStatePub(**kwargs):
    global SYS
    
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']

        #set up zmq context
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.PUB)
        #host publisher on localhost @ port
    socket.bind(f"tcp://127.0.0.1:{port}")

    while True:
        socket.send(
            pickle.dumps(
                json.dumps(
                    {
                        "SYSTEM": SYS,
                        "TIME": TS()
                    }
                )
            )
        )
        await asyncio.sleep(update_tick)
    


