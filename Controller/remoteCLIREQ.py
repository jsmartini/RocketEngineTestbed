import cmd
from config import CONFIG
from time import sleep
import zmq
import pickle
import json
from util import TS

def connect():
    node_name = "Control Computer"
    port = CONFIG["DataConfig"]["CMD_PROMPT_PORT"]
    if int(CONFIG["SIM"]["testing"]) == 1:
        target = CONFIG["NetworkConfig"]["TEST_NETWORK_TARGET"]
    else:
        target = CONFIG["NetworkConfig"]["HARDWARE_NETWORK_TARGET"]

    for i in range(20):

        try:
            ctx = zmq.Context()
            socket = ctx.socket(zmq.REQ)
            socket.connect(f"tcp://{target}:{port}")
            print("RemoteCLI Terminal Connected successfully")
            return socket
        except BaseException as e:
            print(e)
            print(f"Failed to connect on try : {i}")
            sleep(3)
    print("Failed to Establish REP zmq Connection with Sim/hardware")
    exit(-1)

global SOCK
SOCK = connect()

def command(cmd):
    global SOCK
    SOCK.send(
        pickle.dumps(
            json.dumps(
                {
                    "cmd": cmd,
                    "time": TS()
                }
            )
        )
    )
    return json.loads(pickle.loads(SOCK.recv()))

class RemoteCLI(cmd.Cmd):

    prompt = "[TestBed]>"

    def do_enable_2way(self, s):
        print(command("enable_2way"))

    def do_disable_2way(self, s):
        print(command("disable_2way"))

    def do_press(self, s):
        print(command("press"))

    def do_enable2way(self, s):
        print(command("enable_2way"))
    
    def do_disable2way(self, s):
        print(command("disable_2way"))

    def do_depress(self, s):
        print(command("depress"))

    def do_ventlox_open(self, s):
        print(command("ventlox_open"))

    def do_ventlox_close(self, s):
        print(command("ventlox_close"))

    def do_ventkero_open(self, s):
        print(command("ventkero_open"))

    def do_ventkero_close(self, s):
        print(command("ventkero_close"))
    
    def do_ignition(self, s):
        print(command("ignition"))
    
    def do_cmd(self, s):
        rep = command(s)
        for i in rep.keys():
            print(rep[i])


if __name__ == "__main__":
    RemoteCLI().cmdloop()
    



