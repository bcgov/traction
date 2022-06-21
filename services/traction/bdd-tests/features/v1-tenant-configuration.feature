Feature: Tenant Configuration Management
  Scenario: tenant can manage their configuration
    Given we have authenticated at the innkeeper
    And we have "1" traction tenants
     | name  | role    |
     | alice | invitee |
    And innkeeper sets permissions "store_messages" to "True" for "alice"
    And innkeeper sets permissions "store_issuer_credentials" to "True" for "alice"
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
    Then "alice" can update value(s)
    |name|value|
    |store_messages|False|
    And "alice" can get their configuration
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    |auto_respond_messages|False|
    |auto_response_message|my auto response|
    |store_messages|False|
    |store_issuer_credentials|False|
    # if innkeeper disables storage permissions, we cannot set to true
    Then innkeeper sets permissions "store_messages" to "False" for "alice"
    And "alice" cannot update value(s)
    |name|value|
    |store_messages|True|
    Then innkeeper sets permissions "store_issuer_credentials" to "False" for "alice"
    And "alice" cannot update value(s)
    |name|value|
    |store_issuer_credentials|True|
    # but we can update other values
    And "alice" can update value(s)
    |name|value|
    |auto_respond_messages|True|
    And "alice" can get their configuration
    |name|value|
    |webhook_url|None|
    |webhook_key|None|
    |auto_respond_messages|True|
    |auto_response_message|my auto response|
    |store_messages|False|
    |store_issuer_credentials|False|
