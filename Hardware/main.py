from util import *
import asyncio
from config import *
from loadcellpub import *
from pressurepub import *
from system import *
from command import *
from pressurecontrolsub import *

"""

Configure to same execution layout as testmain.py

"""

def blocking_async(thread_loop):
    global CONFIG
    asyncio.set_event_loop(thread_loop)
    remoteCLICoro = remoteCLI(
                node_name = "Remote Command Parser",
                update_tick=0.1,
                port = CONFIG["DataConfig"]["CMD_PROMPT_PORT"]
            )
    print("Running RemoteCLI Daemon")
    thread_loop.run_until_complete(remoteCLICoro)    

def non_blocking_async(thread_loop):
    global CONFIG
    asyncio.set_event_loop(thread_loop)
    thread_loop.run_until_complete(asyncio.gather(
            *[
                SystemStatePub(
                node_name = "System State Reporter",
                update_tick=0.1,
                port = CONFIG["DataConfig"]["SYSTEM_STATE_PORT"]
            ),
            PressureControllerSub(
                node_name = "Pressure PID Controllers",
                update_tick=0.1,
                port = CONFIG["DataConfig"]["PRESSURE_DATAFEED_PORT"]
            ),
            LoadCellPub(
                node_name="Load Cell Sensor Data Aquisition",
                update_tick=0.01,
                cell_name = "Load Sensor 1",
                port = CONFIG["DataConfig"]["LOAD_CELL_DATAFEED_PORT"]
            ),
            PressureDataPub(
                node_name='Pressure Data Aquisition',
                update_tick=0.1, # a tenth of a second latency
                port=CONFIG["DataConfig"]["PRESSURE_DATAFEED_PORT"],
                calibration = CONFIG["PressCalibration"],
                sensor_tuples=[[k,*CONFIG["PressureADCConfig"][k]] for k in CONFIG["PressureADCConfig"]]
            )
            ]
        )
    )

non_blocking_loop = asyncio.new_event_loop()
blocking_loop = asyncio.new_event_loop()
import threading
threading.Thread(target=blocking_async, args=(blocking_loop,), name="RemoteCLI Daemon").start()
threading.Thread(target=non_blocking_async, args=(non_blocking_loop,), name="RemoteCLI Daemon").start()








