import dearpygui.dearpygui as dpg
from config import *
from loadcellSub import *
from pressureSub import *
import datetime
import asyncio
from queue import deque

TS = lambda: datetime.datetime.now().timestamp()
global pressure_data
global loadcell_data

pressure_data = PressureRecorder(
    filename = f"PressureData-{TS()}.dat",
    header = ["Time", "LoxPressure(PSI)", "KeroPressure(PSI)"],
    update_tick=0.1,
    port=CONFIG["DataConfig"]["PRESSURE_DATAFEED_PORT"]
)
loadcell_data = LoadCellRecorder(
    filename = f"LoadCellData-{TS()}.dat",
    header = ["Time", "Voltage Ratio (V)"],
    update_tick=0.1,
    port=CONFIG["DataConfig"]["LOAD_CELL_DATAFEED_PORT"]
)

"""
# load system status subscriber

# load remoteCLI REQ/REP terminal or control panel

#================================================================
# Real Time Plotting of PID Error and Data Points for LOX/KERO Tanks

# dpg value ids
KERO_READING_UUID = dpg.generate_uuid()
LOX_READING_UUID = dpg.generate_uuid()
KERO_ERROR_UUID = dpg.generate_uuid()
LOX_ERROR_UUID = dpg.generate_uuid()
LOADCELL_UUID = dpg.generate_uuid()

# generator functions to aquire and reset plotted data with updated data
def plot_update_pressure_f():
    # generator to update plots for pressure data streams
    global pressure_data
    buffsize = 0.1 * 1000 
    # updates every 0.1 seconds so show 100 seconds
    # buffers to hold plot data
    TIME = deque(buffsize)
    LOX_Reading = deque(buffsize)
    KERO_Reading = deque(buffsize)
    LOX_ERROR = deque(buffsize)
    KERO_ERROR = deque(buffsize)

    while True:
        # update deques with current values
        data, TIME_nxt = pressure_data.current().values()
        TIME.append(TIME_nxt)
        LOX_Reading.append(data["LOX_PSI"])
        KERO_Reading.append(data["KERO_PSI"])
        LOX_ERROR.append(data["LOX_ERROR"])
        KERO_ERROR.append(data["KERO_ERROR"])
        # reset data in dearpygui
        dpg.set_value(KERO_READING_UUID, [TIME, KERO_Reading])
        dpg.set_value(LOX_READING_UUID, [TIME, LOX_Reading])
        dpg.set_value(KERO_ERROR_UUID, [TIME, KERO_ERROR])
        dpg.set_value(LOX_ERROR_UUID, [TIME, LOX_ERROR])
        # make this a generator
        yield 

def plot_update_loadcell_f():
    # generator to update plots to update load cell voltage ratio graph
    global loadcell_data
    buffsize = 0.1 * 1000
    TIME = deque(buffsize)
    LOADCELLDATA = deque(buffsize)

    while True:
        # update current load cell data queue
        _, _, voltage, TIME_nxt = loadcell_data.current().values()
        LOADCELLDATA.append(voltage)
        TIME.append(TIME_nxt)
        dpg.set_value(LOADCELL_UUID, [TIME, LOADCELLDATA])
        
        yield

with dpg.window(label="Rocket Engine Control Dashboard") as main_window:
    pass

# Pressure Monitor Plot
with dpg.window(label="Real Time Pressure Monitor") as pressure_monitor_window:

    with dpg.add_plot(label="Pressure Monitor (PSI)", height=400, width = 400):
        # Time
        dpg.add_plot_axis(dpg.mvXAxis, label="TIME")
        
        # pressure plotting
        dpg.add_plot_axis(dpg.mvYAxis, label = "Pressure (PSI)")
        dpg.add_line_series([], [], label="Kero Tank", parent=dpg.last_item(), id=KERO_READING_UUID)
        dpg.add_line_series([], [], label="Lox Tank", parent=dpg.last_item(), id=LOX_READING_UUID)
        
        # PID Error Plotting
        dpg.add_plot_axis(dpg.mvXAxis, label = "PID Error Pressure (PSI)")
        dpg.add_line_series([], [], label="Kero Tank Error", parent=dpg.last_item(), id=KERO_ERROR_UUID)
        dpg.add_line_series([], [], label="Lox Tank Error", parent=dpg.last_item(), id=LOX_ERROR_UUID)

# load cell monitor plot
with dpg.window(label="Load Cell Data Monitor") as load_cell_monitor:
    dpg.add_plot_axis(dpg.mvXAxis, label="Time")
    dpg.add_plot_axis(dpg.mvYAxis, label="Load Cell Voltage Ratio (V)")    
    dpg.add_line_series([], [], label="Load Cell Data", parent=dpg.last_item(), id=LOADCELL_UUID)


#================================================================
# System Input/Output Prompts




# ================================================================
# implement system status display with indicator lights




# ================================================================
# implement terminal for issuing commands (or control panel)

#================================================================
# ssh terminal to box

# ================================================================
# implement kill button for emergency kill sequence

if __name__ == "__main__":

    async def update_data(tick = 0.1):
        # updates monitor window lines
        while True:

            plot_update_loadcell_f()
            plot_update_pressure_f()

            await asyncio.sleep(tick)

    run_async = lambda: asyncio.gather(*[loadcell_data.sub(), pressure_data.sub(), update_data()])
    asyncio.run_until_complete(run_async())
    dpg.set_primary_window(main_window, True)
    dpg.start_dearpygui()

"""
run_async = lambda: asyncio.gather(*[loadcell_data.sub(), pressure_data.sub()])
asyncio.get_event_loop()\
       .run_until_complete(run_async())
