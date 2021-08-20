from util import *
import asyncio
from config import *
from system import *
from command import *
from testingDataFeed import *

# load gibberish testing publishers with read configuration 
PressureDataPub = lambda: testing_pub(
    node_name='Pressure Data Aquisition',
    update_tick=0.1, # a tenth of a second latency
    port=CONFIG["DataConfig"]["PRESSURE_DATAFEED_PORT"],
    calibration = 0,
    sensor_tuples=[[k,*CONFIG["PressureADCConfig"][k]] for k in CONFIG["PressureADCConfig"]],

    data_generator = pressure_data_generator
)

LoadCellPub = lambda : testing_pub(
    node_name="Load Cell Sensor Data Aquisition",
    update_tick=0.01,
    cell_name = "Load Sensor 1",
    port = CONFIG["DataConfig"]["LOAD_CELL_DATAFEED_PORT"],

    data_generator = loadcell_data_generator
)

def non_blocking_async(thread_loop):
    global CONFIG
    asyncio.set_event_loop(thread_loop)
    print("Running Data Aquisition Daemons")
    thread_loop.run_until_complete(asyncio.gather(
            *[
                PressureDataPub(),
                LoadCellPub(),
                SystemStatePub(
                    node_name = "System State Reporter",
                    update_tick=0.1,
                    port = CONFIG["DataConfig"]["SYSTEM_STATE_PORT"]
                ),
                
            ]
        )
    )

def blocking_async(thread_loop):
    global CONFIG
    asyncio.set_event_loop(thread_loop)
    # create coroutine
    remoteCLICoro = remoteCLI(
                node_name = "Remote Command Parser",
                update_tick=0.1,
                port = CONFIG["DataConfig"]["CMD_PROMPT_PORT"]
            )
    print("Running RemoteCLI Daemon")
    thread_loop.run_until_complete(asyncio.gather(*[remoteCLICoro]))
    print("Error")

non_blocking_loop = asyncio.new_event_loop()
blocking_loop = asyncio.new_event_loop()
import threading
threading.Thread(target=blocking_async, args=(blocking_loop,), name="RemoteCLI Daemon").start()
print("started blocking async")
threading.Thread(target=non_blocking_async, args=(non_blocking_loop,), name="RemoteCLI Daemon").start()
print("started nonblocking async")






