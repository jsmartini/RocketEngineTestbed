import queue
from tkinter import Label, Button
import tkinter as tk

from multiprocessing import Process

from rpisim.PIN import PIN
from rpisim.constants import FALLING, RISING, MODE_IN, MODE_OUT, MODE_PWM

BUTTON_TEMPLATE = "GPIO{id:02d}\n{direction}={value}"
BUTTON_TEMPLATE_PWM = "GPIO{id:02d}\nPWM={value:.02f}"


class App(Process):
    """
    The process running the GUI, and only the GUI.

    Note that you can NOT call any methods on this class from outside it. Instead, you must add a tuple containing
    `(method_name, args, kwargs)` to the command_pipe.

    Also, we will assume that each channel is in BCM format. Since we do not interact with any outside caller, this is a
    safe assumption.
    """

    def __init__(self, command_queue, in_event_queue):

        # connection to the other process
        self.command_queue = command_queue

        # off-thread callback handling
        self.in_event_queue = in_event_queue

        self.pin_by_channel = {}
        self.button_by_channel = {}

        self.root = None

        self.verbosity = 0

        super().__init__()
        self.start()

    def run_command(self):
        """
        Receive a command from the queue and run it.
        """

        commands = {
            '': self.command_null,
            "setup out channel": self.command_setup_out,
            "setup in channel": self.command_setup_in,
            "set out channel": self.command_set_out_value,
            "set verbosity": self.command_set_verbosity,
            "setup pwm": self.command_setup_pwm,
            "update pwm": self.command_update_pwm,
        }

        while True:
            try:
                command, args, kwargs = self.command_queue.get(False)
            except queue.Empty:
                break

            command_func = commands.get(command, self.command_null)
            command_func(command, *args or [], **kwargs or {})

        self.root.after(100, self.run_command)

    def command_null(self, command_name, *args, **kwargs):
        if self.verbosity >= 1:
            print("received unknown command:", command_name, args, kwargs)

    def command_set_verbosity(self, command_name, verbosity):
        self.verbosity = verbosity
        if self.verbosity >= 1:
            print("set output to verbosity", verbosity)

    def command_setup_out(self, command, channel, value):
        if self.verbosity >= 2:
            print("received command:", command, channel, value)
        pin = PIN(MODE_OUT)
        pin.mode = MODE_OUT
        pin.value = value
        self.pin_by_channel[channel] = pin
        self.redraw_out(channel)

    def command_setup_in(self, command, channel, value):
        if self.verbosity >= 2:
            print("received command:", command, channel, value)
        pin = PIN(MODE_IN, value)
        self.pin_by_channel[channel] = pin
        self.setup_in(channel, value)

    def command_set_out_value(self, command, channel, value):

        if self.verbosity >= 4:
            print("setting output {} to {}".format(channel, value))
        pin = self.pin_by_channel[channel]
        pin.value = value

        self.redraw_out(channel)

    def command_setup_pwm(self, command, channel, freq):
        if self.verbosity >= 3:
            print("set up PWM on {} at {} Hz".format(channel, freq))
        pin = self.pin_by_channel[channel]
        pin.mode = MODE_PWM
        pin.freq = 0
        pin.value = 0

        self.update_button(channel)

    def command_update_pwm(self, command, channel, freq, dc):
        dc = dc / 100
        if self.verbosity >= 4:
            print("setting PWM on {} at {} Hz to {}".format(channel, freq, dc))
        pin = self.pin_by_channel[channel]
        pin.freq = freq
        pin.value = dc

        self.update_button(channel)

    #
    # interesting UI functions
    def toggle_button(self, channel):
        pin = self.pin_by_channel[channel]

        if pin.value == 1:
            # falling edge
            pin.value = 0
            self.in_event_queue.put((channel, FALLING))
        elif pin.value == 0:
            # rising edge
            pin.value = 1
            self.in_event_queue.put((channel, RISING))

        self.update_button(channel)

    def update_all_buttons(self, event):
        """
        Update all button texts.

        MUST ONLY BE CALLED FROM THE GUI THREAD!.
        This is mainly used as an event function triggered by PWM duty cycle changes.
        """
        for channel in self.pin_by_channel:
            self.update_button(channel)

    def update_button(self, channel):
        """
        Update the labelling and other properties of the button to match the PIN info.

        THIS CODE MUST NEVER BE CALLED FROM A DIFFERENT THREAD, IT WILL HANG!
        """

        pin = self.pin_by_channel[channel]
        button = self.button_by_channel[channel]

        if pin.mode == MODE_IN:
            button["text"] = BUTTON_TEMPLATE.format(
                id=channel, direction="IN", value=pin.value
            )
        elif pin.mode == MODE_OUT:
            button["text"] = BUTTON_TEMPLATE.format(
                id=channel, direction="OUT", value=pin.value
            )
        elif pin.mode == MODE_PWM:
            if pin.freq == 0:
                button.configure(background='DarkOliveGreen4')
                button.configure(activebackground='DarkOliveGreen4')
            else:
                button.configure(background='DarkOliveGreen3')
                button.configure(activebackground='DarkOliveGreen3')
            button["text"] = BUTTON_TEMPLATE_PWM.format(
                id=channel, value=pin.value
            )

    def button_down(self, event):
        channel = event.widget.GPIO_id
        self.toggle_button(channel)

    def button_up(self, event):
        channel = event.widget.GPIO_id
        self.toggle_button(channel)

    #
    # boring UI functions

    def redraw_out(self, channel):

        pin = self.pin_by_channel[channel]
        btn = self.button_by_channel[channel]

        if pin.mode == MODE_OUT:
            btn["text"] = BUTTON_TEMPLATE.format(
                id=channel, direction="OUT", value=pin.value
            )
            if pin.value == 1:
                btn.configure(background='tan2')
                btn.configure(activebackground='tan2')
            else:
                btn.configure(background='DarkOliveGreen3')
                btn.configure(activebackground='DarkOliveGreen3')

    def setup_in(self, channel, value):
        btn = self.button_by_channel[channel]
        btn.configure(background='gainsboro')
        btn.configure(activebackground='gainsboro')
        btn.configure(relief='raised')
        btn.configure(bd="1px")
        btn["text"] = BUTTON_TEMPLATE.format(
                id=channel, direction="IN", value=value
            )
        btn.bind("<Button-1>", self.button_down)
        btn.bind("<ButtonRelease-1>", self.button_up)

    def add_label(self, text, color, row, column):
        """
        Add a label to this window.
        """
        l = Label(text=text, fg=color)
        l.grid(row=row, column=column, padx=(10, 10))

    def add_button(self, channel, row, column):
        """Add a button to this window and record its channel."""
        text = BUTTON_TEMPLATE.format(
            id=channel, direction="OUT", value=0
        )
        color = "blue"
        btn = Button(
            text=text,
            fg=color, activeforeground=color,
            padx="1px", pady="1px", bd="0px", relief="sunken")
        btn.GPIO_id = channel
        btn.grid(row=row, column=column, padx=(10, 10), pady=(5, 5))
        self.button_by_channel[channel] = btn

    def window_deleted(self):
        self.root.quit()
        import sys
        sys.exit()

    def run(self):
        root = self.root = tk.Tk()
        root.wm_title("GPIO EMULATOR")
        root.protocol("WM_DELETE_WINDOW", self.window_deleted)

        root.bind('<<GPIO_update_buttons>>', self.update_all_buttons)

        self.add_label("5V", "red", 0, 0)
        self.add_label("5V", "red", 0, 1)
        self.add_label("GND", "black", 0, 2)
        self.add_button(14, 0, 3)
        self.add_button(15, 0, 4)
        self.add_button(18, 0, 5)
        self.add_label("GND", "black", 0, 6)
        self.add_button(23, 0, 7)
        self.add_button(24, 0, 8)
        self.add_label("GND", "black", 0, 9)
        self.add_button(25, 0, 10)
        self.add_button(8, 0, 11)
        self.add_button(7, 0, 12)
        self.add_label("ID_SC", "white", 0, 13)
        self.add_label("GND", "black", 0, 14)
        self.add_button(12, 0, 15)
        self.add_label("GND", "black", 0, 16)
        self.add_button(16, 0, 17)
        self.add_button(20, 0, 18)
        self.add_button(21, 0, 19)

        # ###################
        # bottom row

        self.add_label("3V3", "dark orange", 1, 0)
        self.add_button(2, 1, 1)
        self.add_button(3, 1, 2)
        self.add_button(4, 1, 3)
        self.add_label("GND", "black", 1, 4)
        self.add_button(17, 1, 5)
        self.add_button(27, 1, 6)
        self.add_button(22, 1, 7)
        self.add_label("3V3", "dark orange", 1, 8)
        self.add_button(10, 1, 9)
        self.add_button(9, 1, 10)
        self.add_button(11, 1, 11)
        self.add_label("GND", "black", 1, 12)
        self.add_label("ID_SC", "white", 1, 13)
        self.add_button(5, 1, 14)
        self.add_button(6, 1, 15)
        self.add_button(13, 1, 16)
        self.add_button(19, 1, 17)
        self.add_button(26, 1, 18)
        self.add_label("GND", "black", 1, 19)

        root.geometry("+%d+%d" % (0, 0))
        self.root.after(100, self.run_command)

        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass
