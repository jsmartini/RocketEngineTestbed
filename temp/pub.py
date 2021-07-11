import zmq
import asyncio
import pickle
import json
import datetime

TS = lambda: datetime.datetime.now().timestamp()

async def pub(**kwargs):
    node_name = kwargs['node_name']
    port = kwargs['port']
    update_tick = kwargs['update_tick']

    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)

    socket.bind(f"tcp://127.0.0.1:{port}")

    while True:

        
        socket.send(
            pickle.dumps(
                json.dumps(
                    {
                        "node_name": node_name,
                        "time": TS()
                    }
                )
            )
        )
        print(TS())
        
        await asyncio.sleep(update_tick)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            *[pub(
                node_name = "pub eg",
                port = 1069,
                update_tick = 0.1
            )]
        )
    )