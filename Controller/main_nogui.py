
from config import *
#from loadcellSub import *
#from pressureSub import *


from influxRecorder import InfluxRecorderPressure as PressureRecorder
from influxRecorder import InfluxRecorderLoadCell as LoadCellRecorder

import datetime
import asyncio
from queue import deque
from remoteCLIREQ import *

TS = lambda: datetime.datetime.now().timestamp()
global pressure_data
global loadcell_data

global testname

testname = input("Name of this test?>")

def recorders(thread_loop):
    print("Recording Daemon Started")
    asyncio.set_event_loop(thread_loop)
    pressure_data = PressureRecorder(
        filename = f"PressureData-{testname}.dat",
        header = ["Time", "LoxPressure(PSI)", "KeroPressure(PSI)"],
        update_tick=0.1,
        port=CONFIG["DataConfig"]["PRESSURE_DATAFEED_PORT"]
    )
    loadcell_data = LoadCellRecorder(
        filename = f"LoadCellData-{testname}.dat",
        header = ["Time", "Voltage Ratio (V)"],
        update_tick=0.1,
        port=CONFIG["DataConfig"]["LOAD_CELL_DATAFEED_PORT"]
    )
    run_async = lambda: asyncio.gather(*[loadcell_data.sub(), pressure_data.sub()])
    thread_loop.run_until_complete(
        run_async()
    )


if __name__ == '__main__':
    banner = r"""
    No Gui Static Testbed Control Software (client)
    ______ _   _______ _____ _   _ _____   _____ ______________  ___
    | ___ \ | / /_   _|  ___| \ | |  __ \ |_   _|  ___| ___ \  \/  |
    | |_/ / |/ /  | | | |__ |  \| | |  \/   | | | |__ | |_/ / .  . |
    |    /|    \  | | |  __|| . ` | | __    | | |  __||    /| |\/| |
    | |\ \| |\  \ | | | |___| |\  | |_\ \   | | | |___| |\ \| |  | |
    \_| \_\_| \_/ \_/ \____/\_| \_/\____/   \_/ \____/\_| \_\_|  |_/

    Jonathan Martini | Alabama Rocketry Association 2021 | ROLL TIDE!
    """
    from time import sleep
    import threading

    print(banner)
    recording_async_loop = asyncio.new_event_loop()
    recorders = threading.Thread(target=recorders, args=(recording_async_loop,), name="recorders")
    recorders.start()
    sleep(1.5)
    RemoteCLI().cmdloop()
    recorders.stop()

