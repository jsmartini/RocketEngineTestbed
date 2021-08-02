import dearpygui.dearpygui as dpg

global basic_uuid
basic_uuid = dpg.generate_uuid()

from random import random
from queue import deque
import datetime

TS = lambda: datetime.datetime.now().timestamp()

print(open)

def update_plot():
    global basic_uuid
    buff = deque(128)
    t = deque(128)

    while 1:
        buff.append(random())
        t.append(TS())

        dpg.set_value(basic_uuid, [list(t), list(buff)])

        yield

with dpg.window(label="plot"):
    with dpg.add_plot(label="randomasdf", height=400, width = 400):
        dpg.add_plot_axis(dpg.mvXAxis, label="time")
        dpg.add_plot_axis(dpg.mvYAxis, label="randomfgsdfg")
        dpg.add_line_series([0], [0], label = "random", parent=dpg.last_item(), id = basic_uuid)

import asyncio

async def update():
    while True:
        update_plot()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
dpg.start_dearpygui()
#loop.run_until_complete(update)

