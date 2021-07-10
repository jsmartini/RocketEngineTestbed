import zmq
import pickle
import json
import asyncio
from util import *

pl = lambda : "placeholder"

global commmands
commmands = {
    "ventlox": pl,          # vents lox
    "ventkero": pl,         # vents kero
    "ignition": pl,         # starts ignition
    "fuck": pl,             # aborts everything and locks down
    "cleanup": pl           # runs the cleanup procedure
}

# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/client_server.html

def execute(cmd):
    global commands
    if cmd in commands.keys():
        commmands[cmd]()
        return "Executed"
    else:
        return "No Command Found"


async def remoteCLI(**kwargs):
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
        #set up zmq context
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.REP)
        #host publisher on localhost @ port
    socket.bind(f"tcp://127.0.0.1:{port}")

    while True:

        """
        
        command packet


            REQ
        {
            cmd: str,
            time: float
        }

            RES

        {
            cmd: str
            status: bool,
            time: float
        }


        """

        cmd = socket.recv()
        socket.send(
            pickle.dumps(
                json.dumps(
                    {
                        "cmd": cmd["cmd"],
                        "status": execute(cmd["cmd"]),
                        "time": TS()
                    }
                )
            )
        )

        await asyncio.sleep(update_tick)



