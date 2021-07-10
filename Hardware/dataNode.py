import zmq
import time
import logging
import pickle
import json
from queue import deque
import asyncio

# too complicated, good resource tho


class DataPublisher(object):
    """
        For Sensor Data and System State Data
            non-stop publishing to client
    """

    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        self.update_tick = kwargs['update_tick']
        
        #set up zmq context
        port = kwargs['port']
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.PUB)
        #host publisher on localhost @ port
        self.socket.bind(f"tcp://127.0.0.1:{port}")
        
        #holds messages if system can't keep up
        self.stack = deque(kwargs["buffer_size"])

    def push(self, data:dict) -> bool:
        try:
            self.stack.append(
                pickle.dumps(
                    json.dumps(data)
                    )
                )
        except BaseException as e:
            print(e)
            return False
        return True

    async def pubthread(self):
        # runs the service
        while True:
            if (data := self.stack.popleft()) != None:
                self.socket.send(data)
            await asyncio.sleep(self.update_tick)

class DataSubscriber(object):

    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        self.update_tick = kwargs['update_tick']
        
        #set up zmq context
        target = kwargs['target']
        port = kwargs['port']
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBCRIBE, '')
        # subcriber on localhost @ port
        try:
            self.socket.connect(f"tcp://{target}:{port}")
        except zmq.exceptions.ConnectionError as e:
            print(e)
            input(f"@ {self.node_name}: {target}:{port} zmq")
        #holds messages if system can't keep up
        self.stack = deque(kwargs["buffer_size"])

    def pull(self) -> dict:
        try:
            return dict.from_json(
                pickle.loads(
                    self.stack.popleft()
                    )
                )
        except BaseException as e:
            return False

    async def subthread(self):
        while True:
            self.stack.append(
                json.loads(
                    pickle.loads(
                        self.socket.recv()
                    )
                )
            )
            await asyncio.sleep(self.update_tick)
