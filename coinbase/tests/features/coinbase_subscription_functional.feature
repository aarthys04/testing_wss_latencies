Feature: Functional Testing of Coinbase Ticker Subscription

  Scenario: Subscribe to coinbase ticker and validate Successful Subscription
    Given the WebSocket connection to Coinbase ticker is established
    When the user subscribes to ticker updates for a specific product
    Then the subscription message is received with expected fields
    And the ticker messages are received continuously
    And ticker messages should contain the expected fields
    And close connection

  Scenario: Validate error message on trying to subscribe with network issues
    Given the WebSocket connection to Coinbase ticker is established
    When simulating network issues
    Then verify that an error message is received


# Error scenarios [Not implemented]
#  Scenario: Validate error message on trying to subscribe to invalid ticker channel
#    Given the WebSocket connection to Coinbase ticker is established
#    When subscribing to an invalid ticker channel
#    Then verify that an error message is received
#    And validate the error message fields
#
#  Scenario: Validate error message on trying to subscribe with invalid authentication
#    When the user attempts to establish a WebSocket connection with invalid credentials or incorrect URL
#    When attempting to subscribe
#    Then verify that an error message is received
#    And validate the error message fields
#

