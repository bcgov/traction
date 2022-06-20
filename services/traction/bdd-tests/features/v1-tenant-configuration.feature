Feature: Tenant Configuration Management
  Scenario: tenant can manage their configuration
    Given we have authenticated at the innkeeper
    And we have "1" traction tenants
     | name  | role    |
     | alice | invitee |
    # return default configuration values
    Then "alice" can get their configuration
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    |auto_respond_messages|True|
    |auto_response_message|None|
    |store_messages|False|
    |store_issuer_credentials|False|
    # update all values in one call
    Then "alice" can update value(s)
    |name|value|
    |webhook_url|http://fake.url|
    |webhook_key|my-key|
    |auto_respond_messages|False|
    |auto_response_message|my auto response|
    |store_messages|True|
    |store_issuer_credentials|True|
    And "alice" can get their configuration
    |name|value|
    |webhook_url|http://fake.url|
    |webhook_key|my-key|
    |auto_respond_messages|False|
    |auto_response_message|my auto response|
    |store_messages|True|
    |store_issuer_credentials|True|
    # update subset of values
    Then "alice" can update value(s)
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    And "alice" can get their configuration
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    |auto_respond_messages|False|
    |auto_response_message|my auto response|
    |store_messages|True|
    |store_issuer_credentials|True|
    # update a single value
    Then "alice" can update value(s)
    |name|value|
    |store_issuer_credentials|False|
    And "alice" can get their configuration
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    |auto_respond_messages|False|
    |auto_response_message|my auto response|
    |store_messages|True|
    |store_issuer_credentials|False|
