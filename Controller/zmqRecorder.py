import zmq
from recorder import Recorder
from config import *
import json
import pickle
from queue import deque
import asyncio


class ZMQRecorder(Recorder):

    def __init__(self, **kwargs):
        global CONFIG
        super(ZMQRecorder, self).__init__(**kwargs)
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.SUB)
        success = False
        while not success:
            try:
                if int(CONFIG["SIM"]["testing"]) != 1:
                    self.socket.connect(f"tcp://{CONFIG['NetworkConfig']['HARDWARE_NETWORK_TARGET']}:{kwargs['port']}")
                else:
                    self.socket.connect(f"tcp://{CONFIG['NetworkConfig']['TEST_NETWORK_TARGET']}:{kwargs['port']}")
                self.socket.subscribe("")
                success = True
            except BaseException as e:
                print(e)
                print(self.__class__.__name)
                if (dec:=input("Try to Connect Again (y/n)")) != "y": exit(-1)

        print(f"Loaded {self.__class__.__name__} Recorder successfully")
        self.update_tick = kwargs['update_tick']
        self.current_datafeed = deque() # for real time data visualization
        
    def current(self):
        return self.current_datafeed.popleft()

    async def sub(self):

        while True:
            data = json.loads(
                        pickle.loads(
                            self.socket.recv()
                        )
                    )
            
            #print(data.values()) debug
            self.current_datafeed.append(data)

            # this is a major bug - doesnt write to csv in correct format 
            self([str(i) for i in list(data.values())])    # record data into csv file
            await asyncio.sleep(self.update_tick)

