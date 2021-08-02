import threading

from multiprocessing import Queue

from rpisim import gui
from .PIN import PIN
from .TypeChecker import typeassert
from . import pwm

from .constants import BOARD, BCM, LOW, HIGH, MODE_OUT, MODE_IN, PUD_DOWN, PUD_UP, PHYS_TO_BCM_MAP, GPIONames, \
    RISING, FALLING, BOTH

pin_by_channel = {}

# GPIO state, it is a module_wide singleton because that's how the hardware works
_mode = BOARD
_verbosity = 0


def to_BCM_channel(channel):
    """
    Make sure `channel` is a GPIO channel number, even if mode is set to BOARD.
    """
    if _mode == BOARD:
        if channel not in PHYS_TO_BCM_MAP:
            raise KeyError('unknown channel "{}"'.format(channel))
        return PHYS_TO_BCM_MAP[channel]
    elif _mode == BCM:
        return channel
    else:
        raise Exception('GPIO set to unknown mode')


class GPIOEventHandler(threading.Thread):
    """
    Handles all events and callbacks generated by the GPIO process.
    """

    def __init__(self, queue):
        super().__init__(daemon=True)
        self.queue = queue

        self.event_listeners = {pin: [] for pin in GPIONames}
        self.event_detection = {pin: None for pin in GPIONames}
        self.event_detected = {pin: False for pin in GPIONames}

        self.start()

    def add_event_detect(self, channel, edge, callback=None, bouncetime=None):
        """
        Enable event-detection for a given pin.

        `callback` is called on the main GUI thread, so the GUI might block if you do a lot of stuff there.
        `bouncetime` is ignored since we don't have bouncy buttons here.
        """

        # this is just so we can filter by the relevant edges
        self.event_detection[channel] = edge

        if callback:
            self.event_listeners[channel].append(callback)

    def event_detected(self, channel):
        """
        Event polling function. You must enable event detection using `add_event_detect` first.
        """
        res = self.event_detected[channel]
        self.event_detected[channel] = False
        return res

    def run(self):

        while True:
            channel, edge = self.queue.get()
            if _verbosity >= 3:
                print("event: {} {}".format(channel, edge))
            pin = pin_by_channel[channel]
            if edge == RISING:
                pin.value = 1
            else:
                pin.value = 0

            for callback in self.event_listeners[channel]:

                if self.event_detection[channel] in (edge, BOTH):
                    self.event_detected[channel] = True
                    try:
                        if _verbosity >= 3:
                            print("entering callback")
                        callback(channel)
                        if _verbosity >= 3:
                            print("exiting callback")
                    except Exception as e:
                        if _verbosity >= 1:
                            print("callback exited with exception:", e)


################################
# application structure setup
command_queue = Queue()
callback_queue = Queue()

# note that the _app object cannot be read or written, since it resides in a different process
# interaction with it MUST go through the command_pipe and the callback_queue
_app = gui.App(command_queue, callback_queue)

callback_handler = GPIOEventHandler(callback_queue)


#######################
# GPIO LIBRARY Functions
@typeassert(int)
def setmode(mode):
    global _mode
    _mode = mode


@typeassert(bool)
def setwarnings(flag):
    pass


# @typeassert(int, int, int, int)
def setup(channel, state, initial=None, pull_up_down=None):

    channel = to_BCM_channel(channel)

    if channel not in GPIONames:
        raise Exception('GPIO {} does not exist'.format(channel))

    # check if channel is already setup
    if channel in pin_by_channel:
        raise Exception('GPIO is already setup')

    if state == MODE_OUT:
        # GPIO is set as output, default OUT 0
        pin = PIN(MODE_OUT)
        if initial == HIGH:
            pin.value = 1

        pin_by_channel[channel] = pin
        command_queue.put(("setup out channel", (channel, pin.value), None))

    elif state == MODE_IN:
        # set input
        pin = PIN(MODE_IN)
        if pull_up_down is None or pull_up_down == PUD_DOWN:
            pin.pull_up_down = PUD_DOWN
            pin.value = 0
        elif pull_up_down == PUD_UP:
            pin.pull_up_down = PUD_UP
            pin.value = 1

        pin_by_channel[channel] = pin
        command_queue.put(("setup in channel", (channel, pin.value), None))


@typeassert(int, int)
def output(channel, value):

    channel = to_BCM_channel(channel)

    if channel not in pin_by_channel:
        # if channel is not set up
        raise Exception('GPIO must be setup before used (channel {})'.format(channel))
    else:
        pin = pin_by_channel[channel]
        if pin.mode == MODE_IN:
            # if channel is set up as IN and used as an OUTPUT
            raise Exception('GPIO must be setup as OUT (channel {})'.format(channel))

    if value != LOW and value != HIGH:
        raise Exception('Output must be set to HIGH/LOW (channel {}), was set to {}'.format(channel, value))

    pin = pin_by_channel[channel]
    if value == LOW:
        pin.value = 0
    elif value == HIGH:
        pin.value = 1

    command_queue.put(("set out channel", (channel, pin.value), None))


@typeassert(int)
def input(channel):

    channel = to_BCM_channel(channel)

    if channel not in pin_by_channel:
        # if channel is not setup
        raise Exception('GPIO must be setup before used')

    pin = pin_by_channel[channel]
    if pin.mode != MODE_IN:
        # if channel is setup as OUTPUT and used as an INPUT
        raise Exception('GPIO must be setup as IN')

    pin = pin_by_channel[channel]
    if pin.value == 1:
        return True
    elif pin.value == 0:
        return False


def wait_for_edge(channel, edge):
    """
    Block until an event was detected of type `edge` on pin `channel`.
    """
    # TODO: implement edge waiting
    # TODO: how?!
    raise NotImplementedError


add_event_detect = callback_handler.add_event_detect
event_detected = callback_handler.event_detected


def PWM(channel, frequency):
    pin = pin_by_channel[to_BCM_channel(channel)]
    return pwm.PWM(command_queue, pin, channel, frequency)


def cleanup():
    # instead of hard-terminating the process we could also send a command telling it to shut down, but it's not really
    # necessary to do that
    _app.terminate()
    pass


#################################################
# debugging functions
# these do not exist in the regular GPIO library
def set_verbosity(verbosity=4):
    """
    Enable or disable verbose output. Set it to a number, the higher the more output you'll see.

    Here's an overview over the levels:
    0: nothing
    1: warnings and errors
    2: setup tracing
    3: event tracing
    4: output tracing

    """
    global _verbosity
    _verbosity = verbosity
    command_queue.put(("set verbosity", (verbosity, ), None))
