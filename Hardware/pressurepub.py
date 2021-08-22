import zmq
import asyncio
import sys
import os
#from pipyadc.ADS1256_definitions import *
from pipyadc import *
from adcDefinitions import *
#from pipyadc import ADS1256
from util import *
import pickle
import json
from collections import deque
import numpy as np
from config import *
from functools import lru_cache

global CURRENT_PRESSURE_READINGS
CURRENT_PRESSURE_READINGS = {
                "LOX_PSI": 0,
                "KERO_PSI": 0
            }

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
    socket.bind(f"tcp://*:{port}")

    calibration = kwargs['calibration']

    ADS = ADS1256()
    
    sensor_tuples = kwargs['sensor_tuples']
    # example sensor tuple (name, positive connection, negative connection)
    try:

        ADC_channels = [create_diff(t[1], t[2]) for t in sensor_tuples]
        ADC_channel_names = [t[0] for t in sensor_tuples]

    except BaseException as e:
        print(e)
        exit(-1)
    del sensor_tuples

    calc_m_b = lambda vals: (
        (vals[3] - vals[1]) / (vals[2] - vals[0]),  # M
        vals[4]                                     # B
    )

    sensor_calibration = [CONFIG["PressureCalibration"][k] for k in CONFIG["PressureCalibration"].keys()]
    sensor_calibration = [calc_m_b(mb) for mb in sensor_calibration]

    ma_max_len = CONFIG["MA"]["MA_FILTER_LEN"]
    sensor_lox = deque(maxlen=ma_max_len)
    sensor_kero = deque(maxlen=ma_max_len)

    def MA(nxt, history):
        history.append(nxt)
        return np.average(history)
    
    scale = lambda v, m, b: m*v + b

    filters = {
            "KERO_PSI": lambda x: MA(x, history=sensor_lox),
            "LOX_PSI": lambda x: MA(x, history=sensor_kero)
        }
        
    def scaleNSmooth(inp: list, names = ADC_channel_names, calibration = calibration):
        # scales incoming voltages and outputs dict of sensor: PSI reading
        global CURRENT_PRESSURE_READINGS
        
        set_l = len(set(names))
        l     = len(names)
        flag  = set_l < l
        if True:    # i dont remember the short cut to tab things left
            KERO_PSI, LOX_PSI = 0, 0
            if flag:
                KERO = []
                LOX = []
                for v, n in zip(inp, names):
                    if "KERO_PSI" in n :
                        KERO.append(v)
                    else:
                        LOX.append(v)
                KERO_PSI = next(filters["KERO_PSI"](np.average(KERO)))
                LOX_PSI = next(filters["LOX_PSI"](np.average(LOX)))
            else:
                for v, n, consts in zip(inp, names, sensor_calibration):
                    if "KERO_PSI" in n:
                        KERO_PSI = scale(filters["KERO_PSI"](v), *consts)
                    else:
                        LOX_PSI = scale(filters["LOX_PSI"](v), *consts)
            return{
                "LOX_PSI": LOX_PSI,
                "KERO_PSI": KERO_PSI
            }

    while True:
        t = TS()
        data = scaleNSmooth(ADS.read_sequence(ADC_channels))
        data = {
                        "LOX_PSI": data["LOX_PSI"],
                        "KERO_PSI": data["KERO_PSI"],
                        
        }
        CURRENT_PRESSURE_READINGS = data
        data["TIME"] = t
#        print(CURRENT_PRESSURE_READINGS)
        socket.send(
            pickle.dumps(
                json.dumps(
                    data
                )
            )
        )
        await asyncio.sleep(update_tick)

if __name__ == "__main__":
    # verification code
    zero = (-943, 0)
    point = (1873, 100)
    m = (point[0]-zero[0])/(point[1])
    b = -22

    scale = lambda val: val/m - b
    ADS = ADS1256()
    ch = [create_diff(7,6)]
    while True:
        print(scale(ADS.read_sequence(ch)[0]))
