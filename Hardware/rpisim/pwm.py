from rpisim.constants import MODE_PWM


class PWM:

    def __init__(self, command_pipe, pin, channel, freq):
        self.command_pipe = command_pipe
        self.channel = channel
        self.freq = freq
        self.dc = 0
        self.pin = pin

        pin.mode = MODE_PWM
        #print("setup PWM on {} @ {} Hz".format(bcm_channel, freq))

        command_pipe.put(("setup pwm", (channel, freq), None))

    def start(self, dc):
        self.dc = dc
        #print("starting PWM on {} @ {} Hz, dc = {} %".format(
        #    self.bcm_channel, self.freq, dc)
        #)
        self.pin.value = dc / 100
        self.command_pipe.put((
            'update pwm',
            (self.channel, self.freq, self.dc),
            None
        ))

    def stop(self):
        self.command_pipe.put((
            'update pwm',
            (self.channel, 0, self.dc),
            None
        ))

    def ChangeDutyCycle(self, dc):
        # print("pwm on {}: {} %".format(self.bcm_channel, dc))
        self.dc = dc
        self.pin.value = dc / 100
        self.command_pipe.put((
            'update pwm',
            (self.channel, self.freq, self.dc),
            None
        ))

    def ChangeFrequency(self, freq):
        self.freq = freq
        self.command_pipe.put((
            'update pwm',
            (self.channel, self.freq, self.dc),
            None
        ))
