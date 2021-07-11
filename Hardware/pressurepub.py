import zmq
import asyncio
import sys
import os
from pipyadc.ADS1256_definitions import *
from pipyadc import ADS1256
from util import *
import pickle
import json



def create_diff(inp1, inp2):
	# configures ADC_channels
    terminals = {
        "0": (POS_AIN0, NEG_AIN0),
        "1": (POS_AIN1, NEG_AIN1),
        "2": (POS_AIN2, NEG_AIN2),
        "3": (POS_AIN3, NEG_AIN3),
        "4": (POS_AIN4, NEG_AIN4),
        "5": (POS_AIN5, NEG_AIN5),
        "6": (POS_AIN6, NEG_AIN6),
        "7": (POS_AIN7, NEG_AIN7),
        }
    return terminals[str(inp1)][0] | terminals[str(inp2)][1]

async def PressureDataPub(**kwargs):
    node_name = kwargs['node_name']
    update_tick = kwargs['update_tick']
        #set up zmq context
    port = kwargs['port']
    ctx = zmq.Context()
    socket =  ctx.socket(zmq.PUB)
        #host publisher on localhost @ port
    socket.bind(f"tcp://127.0.0.1:{port}")

    calibration = kwargs['calibration']

    ADS = ADS1256()

    
    sensor_tuples = kwargs['sensor_tuples']
    # example sensor tuple (name, positive connection, negative connection)
    ADC_channels = [create_diff(t[1], t[2]) for t in sensor_tuples]
    ADC_channel_names = [t[0] for t in sensor_tuples]
    del sensor_tuples

    def scaleNSmooth(inp: list, names = ADC_channel_names, calibration = calibration):
        # scales incoming voltages and outputs dict of sensor: PSI reading
        return {
            "Time": 0,
            "LOX_PSI": 0,
            "KERO_PSI": 0
        }

    while True:
        socket.send(
            pickle.dumps(
                json.dumps(
                    {
                        "DATA": scaleNSmooth(ADS.read_sequence(ADC_channels)),
                        "TIME": TS()
                    }
                )
            )
        )
        await asyncio.sleep(update_tick)







    





