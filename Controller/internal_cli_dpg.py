import dearpygui.dearpygui as dpg
from remoteCLIREQ import command, SOCK

def c2c(cmd, obj_ref):
    # ties in the object to log the command
    obj_ref._log(command(cmd))

class RemoteCLITerminal():

    # https://github.com/hoffstadt/DearPyGui/blob/master/DearPyGui/dearpygui/logger.py

    def __init__(self, parent = None):

        self.log_level = 0
        self._auto_scroll = True
        self.filter_id = None
        if parent:
            self.window_id = parent
        else:
            self.window_id = dpg.add_window(label="Remote CLI Term", pos=(200, 200), width=500, height=500)
        self.count = 0
        self.flush_count = 1000

        with dpg.group(horizontal=True, parent=self.window_id):
            dpg.add_checkbox(label="Auto-scroll", default_value=True, callback=lambda sender:self.auto_scroll(dpg.get_value(sender)))
            dpg.add_button(label="Clear", callback=lambda: dpg.delete_item(self.filter_id, children_only=True))

        dpg.add_input_text(label="Command", callback=lambda msg: c2c(msg, self), 
                    parent=self.window_id)
        self.child_id = dpg.add_child(parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        with dpg.theme() as self.info_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))

    def auto_scroll(self, value):
        self._auto_scroll = value

    def _log(self, message):
        new_log = dpg.add_text(str(message), parent=self.filter_id, filter_key=message)
        dpg.set_item_theme(new_log, self.info_theme)
        if self._auto_scroll:
            scroll_max = dpg.get_y_scroll_max(self.child_id)
            dpg.set_y_scroll(self.child_id, -1.0)

    def clear_log(self):
        dpg.delete_item(self.filter_id, children_only=True)
        self.count = 0

if __name__ == '__main__':
    with dpg.window(label="DPG Internal CLI Demo", width=800, height=800, pos=(100, 100)) as id:
        RemoteCLITerminal(parent=id)