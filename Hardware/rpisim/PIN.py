from rpisim.constants import PUD_OFF, MODE_IN


class PIN:

    def __init__(self, mode, value=None, pull_up_down=None):
        self.mode = mode
        self.pull_up_down = pull_up_down or PUD_OFF
        self.value = value or 0

    def __str__(self):
        return "<PIN {} @ {}>".format(
            "IN" if self.mode == MODE_IN else "OUT",
            self.value,
        )

    def __repr__(self):
        return "PIN({}, {}, {})".format(self.mode, self.value, self.pull_up_down)

