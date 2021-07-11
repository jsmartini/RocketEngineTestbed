import zmq
from recorder import Recorder
from config import *
import json
import pickle
import deque
import asyncio

class ZMQRecorder(Recorder):

    def __init__(self, **kwargs):
        global CONFIG
        super(PressureRecorder, self).__init__(**kwargs)
        ctx = zmq.Context()
        socket = ctx.socket(zmq.SUB)
        try:
            socket.connect(f"tcp://{CONFIG.NetworkConfig.HARDWARE_NETWORK_TARGET}:{kwargs['port']}")
            socket.subscribe("")
        except BaseException as e:
            print(e)
            input("kill due to error")
            exit(-1)

        print("Loaded Pressure Recorder successfully")
        self.update_tick = kwargs['update_tick']
        self.current_datafeed = deque(128) # for real time data visualization
        
    def current(self):
        return self.current_datafeed.popleft()

    async def sub(self):

        while True:
            data = json.loads(
                        pickle.loads(
                            self.socket.recv()
                        )
                    )
            self.current_datafeed.append(data)
            super(data.values())    # record data into csv file
            await asyncio.sleep(self.update_tick)

