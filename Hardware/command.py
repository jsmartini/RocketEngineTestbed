import zmq
import pickle
import json
import asyncio
from util import *
from hardware import *
from pressurecontrolsub import toggle_pid

def kill_tmp():
    lox_entry_close()
    kero_entry_close()

pl = lambda: "place holder function reference"
echo = lambda x: x

global commands
commands = {
    "enable_2way": enable_2way,
    "disable_2way": disable_2way,
    "press": press_propellant_tanks,
    "depress": depress_propellant_tanks,
    "ventlox_open": lox_vent_on,          # vents lox
    "ventlox_close": lox_vent_off,
    "ventkero_open": kero_vent_on,         # vents kero
    "ventkero_close": kero_vent_off,
    "ignition": ignition,         # starts ignition
    "fuck": kill_tmp,             # aborts everything and locks down
    "cleanup": pl,           # runs the cleanup procedure
    "echo": echo,
    "toggle_pid": toggle_pid,
    "kero_entry_open": kero_entry_open,
    "kero_entry_close": kero_entry_close,
    "lox_entry_open": lox_entry_open,
    "lox_entry_close": lox_entry_close,
    "reset": reset_gpio,
}

command_list = lambda : "\n".join(commands.keys())
commands["help"] = command_list

# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/client_server.html

def execute(cmd):
    global commands
    if cmd in commands.keys():
        return f"Executed {commands[cmd]()}"
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
    socket.bind(f"tcp://*:{port}")

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
        
        
        try:
            cmd = json.loads(pickle.loads(socket.recv()))
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
        except BaseException as e:
            print(e)

        await asyncio.sleep(update_tick)



