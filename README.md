# testing_latencies

Locust test script - test_ticker_latencies.py 
On start, establishing connection and sending subscription message
{  "type": "subscribe",       
   "channels": [{ "name": "ticker", 
                   "product_ids": ["BTC-USD"]
               }]    
}

On message received, calculating latencies and sending it to locust by using events.reuest.fire
Run locust test - locust -f ./performance_tests/test_ticker_latencies.py -P 8040 
[-P is optional, it will take default port]Locust test can be run in Kubernetes or using master//worker nodes to distribute the load efficiently while running as soak test with multiple connections -https://docs.locust.io/en/stable/running-distributed.html
get_latencies.py is another way to validate latencies but is not ingreated with any tool and need to explore on ways to save the latencies as storing them in array/list might cause memory issue if we run for long time – Reference [coinbase repo]

