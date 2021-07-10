from util import *
import asyncio
from config import *
from loadcellpub import *
from pressurepub import *
from system import *
from command import *
from pressurecontrolsub import *


async def main():
    """
    
    Initializes ZMQ servers and the pressure controller sub
    

    TODO:

        Split Loadcell, {System, remoteCLI}, and Pressure utilities into own threads and incorporate logging across all nodes
    """

    global CONFIG

    asyncio.gather(
        *[
            PressureDataPub(
                node_name='Pressure Data Aquisition',
                update_tick=0.1, # a tenth of a second latency
                port=CONFIG.DataConfig.PRESSURE_DATAFEED_PORT,
                calibration = CONFIG.PressCalibration,
                sensor_tuples=[[k,*CONFIG.PressureADCConfig[k]] for k in CONFIG.PressureADCConfig]
            ),
            remoteCLI(
                node_name = "Remote Command Parser",
                update_tick=0.1,
                port = CONFIG.DataConfig.CMD_PROMPT_PORT
            ),
            LoadCellPub(
                node_name="Load Cell Sensor Data Aquisition",
                update_tick=0.01,
                cell_name = "Load Sensor 1",
                port = CONFIG.DataConfig.LOAD_CELL_DATAFEED_PORT,
            ),
            SystemStatePub(
                node_name = "System State Reporter",
                update_tick=0.5,
                port = CONFIG.DataConfig.SYSTEM_STATE_PORT
            ),
            PressureControllerSub(
                
            )
        ]
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


