import zmq

from config import *
import json
import pickle
from queue import deque
import asyncio
from influxdb_client import InfluxDBClient

class InfluxRecorderPressure(object):

    def __init__(self, **kwargs):
        global CONFIG
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.SUB)
        self.client = InfluxDBClient(host='localhost', port=8086, username='ara', password='ara')
        self.client.switch_database('ara')
        success = False
        self.name = kwargs["filename"][:-4]
        
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

            influx_fmt = {
                "measurement": "Pressure",
                "tags" : {
                    "testname": self.name
                },
                "time": data["TIME"],
                "fields": {
                    "KERO PSI": data["KERO_PSI"],
                    "LOX PSI": data["LOX_PSI"]
                }
            }

            self.client.write_points([influx_fmt])

            await asyncio.sleep(self.update_tick)


class InfluxRecorderLoadCell(object):

    def __init__(self, **kwargs):
        global CONFIG
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.SUB)
        self.client = InfluxDBClient(host='localhost', port=8086, username='ara', password='ara')
        self.cleint.switch_database('ara')
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

            influx_fmt = {
                "measurement": "Load Cell",
                "tags" : {
                    "testname": self.name
                },
                "time": data["TIME"],
                "fields": {
                    "Voltage": data["VOLTAGE_RATIO"],
                }
            }

            self.client.write_points([influx_fmt])
            # this is a major bug - doesnt write to csv in correct format 

            await asyncio.sleep(self.update_tick)