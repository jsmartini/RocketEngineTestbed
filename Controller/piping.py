import zmq
from typing import Generator
import json
import pickle
import asyncio

# serialization macros
stddump = lambda x: x   # for basic type serialization i.e use json.dumps for dumping dicts
serialize = lambda dumpfunc, data: pickle.dumps(dumpfunc(data))
stdload = stddump
deserialize = lambda loadfunc, data: loadfunc(pickle.loads(data))

async def pub(data_src: Generator, **kwargs):
    # generic pub from generator function to update
    port = kwargs['port']
    tick = kwargs['tick']

    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)

    socket.bind(f"tcp://127.0.0.1:{port}")

    while True:
        socket.send(serialize(data_src()))
        asyncio.sleep(tick)

async def sub(buffer, **kwargs):
    # generic sub function to continually update a referenced buffer
    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)
    target = kwargs['target']
    port = kwargs['port']
    tick = kwargs['tick']
    try:
        socket.connect(f"tcp://{target}:{port}")
        socket.subscribe("")
    except BaseException as e:
        print(e)
        input("kill due to error")
        exit(-1)

    while True:
        buffer.append(deserialize(socket.recv()))
        asyncio.sleep(tick)

