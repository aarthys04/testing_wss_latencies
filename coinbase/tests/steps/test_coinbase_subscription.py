import time
from behave import given, when, then
from helpers.websocket_helper import WebSocketHelper


@given('the WebSocket connection to Coinbase ticker is established')
def step_establish_websocket_connection(context):
    context.ws_url = "wss://ws-feed.pro.coinbase.com"
    context.websocket_helper = WebSocketHelper(context.ws_url)
    context.websocket_helper.connect()
    time.sleep(1) # instead of waits we can assert of connection status
    if context.websocket_helper.ws:
        print("WebSocket connection is open")


@when('the user subscribes to ticker updates for a specific product')
def step_subscribe_to_ticker_updates(context):
    if context.websocket_helper.ws:
        print("WebSocket connection is open")
    else:
        print("WebSocket connection is closed")

    # Send the subscribe message
    context.websocket_helper.send_subscribe_message()


@then('the subscription message is received with expected fields')
def step_validate_subscription_message(context):
    subscription_message = context.websocket_helper.wait_for_subscription_message()
    assert subscription_message is not None, "Subscription message not received"

    # Validate expected fields in the subscription message
    assert subscription_message["type"] == "subscriptions", "Unexpected message type"
    assert "channels" in subscription_message, "Channels field not found"
    assert len(subscription_message["channels"]) == 1, "Unexpected number of channels"
    assert subscription_message["channels"][0]["name"] == "ticker", "Unexpected channel name"
    assert subscription_message["channels"][0]["product_ids"] == ["BTC-USD"], "Unexpected product IDs"


@then('the ticker messages are received continuously')
def check_ticker_messages_continuously(context):
    # Wait for the ticker update messages to be received continuously for a specified duration
    start_time = time.time()
    duration = 10  # Specify the duration in seconds
    ticker_messages = []

    while time.time() - start_time < duration:
        # Wait for the ticker update message to be received
        context.websocket_helper.ticker_update_received_event.wait()

        # Check if the ticker update message was received
        assert context.websocket_helper.ticker_update_message is not None, "Ticker update message not received"

        # Add the ticker update message to the list
        ticker_message = context.websocket_helper.ticker_update_message
        ticker_messages.append(ticker_message)

        # Reset the event for the next ticker update message
        context.websocket_helper.ticker_update_received_event.clear()
    context.ticker_messages = ticker_messages
    # Check if ticker messages were received continuously
    assert len(ticker_messages) > 1, "Only one ticker message received"
    for i in range(len(ticker_messages) - 1):
        # Check if the timestamp of the current message is less than the timestamp of the next message
        assert ticker_messages[i]["time"] <= ticker_messages[i + 1]["time"], "Ticker messages not received continuously"


# Define the expected fields in a ticker message
expected_fields = ["type", "sequence", "product_id", "price", "open_24h", "volume_24h", "low_24h",
                   "high_24h", "volume_30d", "best_bid", "best_bid_size", "best_ask", "best_ask_size",
                   "side", "time", "trade_id", "last_size"]


@then('ticker messages should contain the expected fields')
def validate_ticker_message_fields(context):
    # Check if ticker messages have been received
    assert context.ticker_messages, "No ticker messages received"

    # Iterate through each ticker message and validate the presence of expected fields
    for ticker_message in context.ticker_messages:
        for field in expected_fields:
            assert field in ticker_message, f"Expected field '{field}' not found in ticker message"
            assert ticker_message[field], f"Field '{field}' in ticker message has no value"


@when("simulating network issues")
def step_simulate_network_issues(context):
    # Here you can simulate network issues by disconnecting the WebSocket connection
    try:
        if context.websocket_helper:
            context.websocket_helper.disconnect()
    except Exception as ex:
        print(ex)


@then('verify that an error message is received')
def step_verify_error_message(context):
    time.sleep(1)
    has_error = context.websocket_helper.has_error_occurred()
    assert has_error, "Error message not received"


@then("verify that network error message is received")
def step_verify_error_message(context):
    # Wait for a short time to ensure that the disconnection is completed
    time.sleep(1)
    error_message = context.ws_helper.get_error_message()
    # Check if an error message has occurred
    assert context.websocket_helper.has_error_occurred(), "Error message not received"
    assert error_message is not None, "No error message received"
    assert "Connection to remote host was lost" in error_message, "Unexpected error message"


@then('close connection')
def clean_up(context):
    # close connection to stop receiving messages after test run
    if context.websocket_helper:
        context.websocket_helper.disconnect()
