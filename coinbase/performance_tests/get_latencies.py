import asyncio
import json
import threading
import time
import websockets
from datetime import datetime, timezone

import numpy as np

URI = 'wss://ws-feed.exchange.coinbase.com'

receivedData = []
latencies = []


def calculate_latencies():
    while True:
        if receivedData:
            rxdata = receivedData.pop(0)
            print(rxdata)

            print(f"Median: {np.percentile(latencies, 50)}")
            print(f"90th Percentile: {round(np.percentile(latencies, 90))}")
            print(f"95th Percentile: {round(np.percentile(latencies, 95))}")
            print(f"99th Percentile: {round(np.percentile(latencies, 99))}")
            time.sleep(0.01)


async def websocket_listener():
    test_subscribe_message = json.dumps({
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["ticker"]
    })
    threading.Thread(target=calculate_latencies).start()

    while True:
        try:
            async with websockets.connect(URI, ping_interval=None) as websocket:
                await websocket.send(test_subscribe_message)
                while True:
                    response = await websocket.recv()
                    json_response = json.loads(response)
                    if json_response and json_response.get('time') is not None:
                        resptimestamp = datetime.strptime(str(json_response.get('time')), '%Y-%m-%dT%H:%M:%S.%fZ')
                        latency = round((datetime.now(timezone.utc).timestamp() - resptimestamp.replace(
                            tzinfo=timezone.utc).timestamp()) * 1000)
                        data = {'MsgSequence': json_response.get('sequence'), 'Latency': latency}
                        receivedData.append(data)
                        # Not ideal to store in list as it might exhaust memory as there is no limit to the number of messages we can receive
                        latencies.append(latency)

        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
            print('Connection closed, retrying..')
            await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(websocket_listener())
    except KeyboardInterrupt:
        print("Exiting WebSocket..")
