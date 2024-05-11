from datetime import datetime, timezone
import websocket
import json
import threading
import time


class WebSocketHelper:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.error_occurred = False
        self.error_message = None
        self.connection_established_event = threading.Event()  # Event to signal when connection is established
        self.subscription_received_event = threading.Event()  # Event to signal when subscription message is received
        self.ticker_update_received_event = threading.Event()  # Event to signal when ticker update message is received
        self.subscription_message = None  # Variable to store the received subscription message
        self.ticker_update_message = None  # Variable to store the received ticker update message

    def on_open(self, ws):
        print("WebSocket connection established")
        self.connection_established_event.set()  # Signal that connection is established

    def on_close(self, ws):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.close()
        print("WebSocket connection closed")

    def on_error(self, ws, error):
        # we can define custom exceptions here
        self.error_occurred = True
        self.error_message = error
        print("WebSocket error:", error)

    def has_error_occurred(self):
        if self.error_occurred:
            return self.error_occurred

    def get_error_message(self):
        return self.error_message

    def disconnect(self):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.close()

    def on_message(self, ws, message):
        print("Received message:", message)
        # Attempt to parse message as JSON
        try:
            message_data = json.loads(message)
            # Check if the message contains a "type" field
            if "type" in message_data:
                if message_data["type"] == "subscriptions":
                    print("Subscription message received")
                    self.subscription_message = message_data
                    self.subscription_received_event.set()
                elif message_data["type"] == "ticker":
                    print("Ticker update message received")
                    self.ticker_update_message = message_data
                    self.ticker_update_received_event.set()
        except json.JSONDecodeError:
            pass

    def is_subscription_message(self, message):
        # Implement logic to check if the message is a subscription message
        try:
            message_data = json.loads(message)
            if message_data.get("type") == "subscribe":
                return True
        except json.JSONDecodeError:
            pass
        return False

    def is_ticker_update_message(self, message):
        # Implement logic to check if the message is a ticker update message
        try:
            message_data = json.loads(message)
            if message_data.get("type") == "ticker":
                return True
        except json.JSONDecodeError:
            pass
        return False

    def connect(self):
        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(self.ws_url,
                                         on_open=self.on_open,
                                         on_close=self.on_close,
                                         on_message=self.on_message,
                                         on_error=self.on_error)
        # Run WebSocket connection loop in a separate thread
        websocket_thread = threading.Thread(target=self.ws.run_forever)
        websocket_thread.start()

    def send_subscribe_message(self):
        # Wait for the connection to be established
        if not self.connection_established_event.wait(timeout=5):
            print("WebSocket connection not established within timeout period")
            return

        # Subscribe to ticker updates for BTC-USD product
        subscribe_message = {
            "type": "subscribe",
            "channels": [
                {
                    "name": "ticker",
                    "product_ids": [
                        "BTC-USD"
                    ]
                }
            ]
        }

        self.ws.send(json.dumps(subscribe_message))
        print("Subscribe message sent")

    def wait_for_subscription_message(self, timeout=10):
        # Wait for the subscription message to be received
        if not self.subscription_received_event.wait(timeout=timeout):
            print("Subscription message not received within timeout period")
            return None
        return self.subscription_message

    def wait_for_ticker_update(self, timeout=10):
        # Wait for the ticker update message to be received
        if not self.ticker_update_received_event.wait(timeout=timeout):
            print("Ticker update message not received within timeout period")
            return None
        return self.ticker_update_message

    def ticker_messages(self, timeout=3):
        # Wait for the ticker update messages to be received continuously for a specified duration
        start_time = time.time()
        duration = 10  # Specify the duration in seconds
        ticker_messages = []

        while time.time() - start_time < duration:
            # Wait for the ticker update message to be received
            self.ticker_update_received_event.wait(timeout)

            # Check if the ticker update message was received
            assert self.ticker_update_message is not None, "Ticker update message not received"

            # Add the ticker update message to the list
            ticker_message = self.ticker_update_message
            ticker_messages.append(ticker_message)

            # Reset the event for the next ticker update message
            self.ticker_update_received_event.clear()
        return ticker_messages

    def str_to_utc_time(self, input_time):
        # Assuming ticker_message1["time"] is a string representing a timestamp
        resp_timestamp = datetime.strptime(input_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        return resp_timestamp.replace(tzinfo=timezone.utc).timestamp()
