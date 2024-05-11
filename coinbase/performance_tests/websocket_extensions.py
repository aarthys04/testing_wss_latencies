import json
import websocket
from locust import events
from datetime import datetime, timezone


class WebSocketClient:
    subscribe_message = json.dumps({
            "type": "subscribe",
            "channels": [
                {
                    "name": "ticker",
                    "product_ids": [
                        "BTC-USD"
                    ]
                }
            ]
        })

    def __init__(self, uri, conn_name):
        self.uri = uri
        self.connection_name = conn_name
        
    def on_message(self, ws, message):
        #print(f"Received: {message}")
        json_response = json.loads(message)
        if json_response and json_response.get('time') is not None:    
            print(json_response.get('time'))
            print(datetime.now(timezone.utc))                    
            resptimestamp = datetime.strptime(str(json_response.get('time')), '%Y-%m-%dT%H:%M:%S.%fZ')
            print(f"response_time:{resptimestamp.replace(tzinfo=timezone.utc).timestamp()}")
            print(f"current_time:{datetime.now(timezone.utc).timestamp()}")

            latency = ((datetime.now(timezone.utc).timestamp()-resptimestamp.replace(tzinfo=timezone.utc).timestamp()) * 1000)
            # data = {'msg_sequence' : json_response.get('sequence'), 'latency' : latency}

            print(f"Latency: {latency} ms")
            if latency > 0: # if server clock is ahead or for some reason sometime current time is behind response message time
                events.request.fire(request_type="WebSocket", name=self.connection_name,
                                response_time=latency,
                                response_length=0)

    def on_error(ws, error):
        print(f"Error: {error}")

    def on_close(ws):
        print("Connection closed")

    def on_open(self,ws):
        print("Connection opened")
        ws.send(self.subscribe_message)

    def start(self):
        self.ws = websocket.WebSocketApp(self.uri, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)   
        self.ws.on_open = self.on_open    
        self.ws.run_forever()
