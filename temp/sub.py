import zmq
import pickle
import json
import asyncio

async def sub(**kwargs):
    port = kwargs['port']
    update_tick = kwargs['update_tick']

    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)
    try:

        socket.connect(f"tcp://127.0.0.1:{port}")
        socket.subscribe("")

    except BaseException as e:
        print(e)

    print("running")
    while True:

        data = json.loads(
            pickle.loads(
                socket.recv()
            )
        )

        print(json.dumps(data, indent=4))

        await asyncio.sleep(update_tick)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            *[
                sub(port = 1069, update_tick= 0.1)
            ]
        )
    )