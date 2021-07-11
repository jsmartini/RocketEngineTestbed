from zmqRecorder import ZMQRecorder

class LoadCellRecorder(ZMQRecorder):

    def __init__(self, **kwargs):
        super(LoadCellRecorder, self).__init__(**kwargs)

