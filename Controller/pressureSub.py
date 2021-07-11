from zmqRecorder import ZMQRecorder

class PressureRecorder(ZMQRecorder):

    def __init__(self, **kwargs):
        super(PressureRecorder, self).__init__(**kwargs)

