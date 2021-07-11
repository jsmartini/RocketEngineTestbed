import dearpygui.dearpygui as dpg
from config import *
from loadcellSub import *
from pressureSub import *
import datetime
import asyncio


TS = lambda: datetime.datetime.now().timestamp()


pressure_data = PressureRecorder(
    filename = f"PressureData-{TS()}.dat",
    header = ["Time", "LoxPressure(PSI)", "KeroPressure(PSI)"],
    update_tick=0.1
)
loadcell_data = LoadCellRecorder(
    filename = f"LoadCellData-{TS()}.dat",
    header = ["Time", "Voltage Ratio (V)"],
    update_tick=0.1
)

# run subscribers
run_async = lambda: asyncio.gather(*[loadcell_data.sub(), pressure_data.sub()])



if __name__ == "__main__":
    dpg.start_dearpygui()
    asyncio.run_until_complete(run_async())













dpg.start_dearpygui()