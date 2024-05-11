from locust import User, task
import threading
import performance_tests.websocket_extensions as ws_helper

URI = 'wss://ws-feed.exchange.coinbase.com'


class TestTickerLatencies(User):    
    client1 = ws_helper.WebSocketClient(URI, "client1")
    client2 = ws_helper.WebSocketClient(URI, "client2")

    def start_client1(self):
        self.client1.start()
    
    def on_start(self):
        print("Starting websocket listener: Onstart")
        threading.Thread(target=self.client1.start).start()
        threading.Thread(target=self.client2.start).start()

        print("Starting websocket listener: Threads started")  

    # To run tests
    # locust -f ./performance_tests/test_ticker_latencies.py -P 8036
    # As locust can't start without task being triggered, creating dummy task
    @task
    def send_latencies(self):
        return None

