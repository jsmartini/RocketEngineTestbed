from util import *
import asyncio
from config import *
from loadcellpub import *
from pressurepub import *
from system import *
from command import *
from pressurecontrolsub import *


###############################     SETUP
global CONFIG

# load toml file
CONFIG = load()

# init hardware
init()


async def main():
    """
    
    Initializes ZMQ servers and the pressure controller sub
    

    TODO:

        Split Loadcell, {System, remoteCLI}, and Pressure utilities into own threads and incorporate logging across all nodes
    """
    asyncio.gather(
        *[
            PressureDataPub(

            ),
            remoteCLI(

            ),
            LoadCellPub(

            ),
            SystemStatePub(

            ),
            PressureController(

            )
        ]
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


