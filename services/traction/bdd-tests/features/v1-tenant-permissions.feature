Feature: Innkeeper - Tenant Permissions Management
  Scenario: innkeeper can manage tenant permissions
    Given we have authenticated at the innkeeper
    And we have "1" traction tenants
     | name  | role    |
     | alice | invitee |
    # return default permissions values
    Then innkeeper can get "alice" permissions
    |name|value|
    |endorser_approval|False|
    |create_schema_templates|False|
    |create_credential_templates|False|
    |issue_credentials|False|
    |store_messages|False|
    |store_issuer_credentials|False|
    # update all values in one call
    Then innkeeper can update "alice" permissions
    |name|value|
    |endorser_approval|True|
    |create_schema_templates|True|
    |create_credential_templates|True|
    |issue_credentials|True|
    |store_messages|True|
    |store_issuer_credentials|True|
    And innkeeper can get "alice" permissions
    |name|value|
    |endorser_approval|True|
    |create_schema_templates|True|
    |create_credential_templates|True|
    |issue_credentials|True|
    |store_messages|True|
    |store_issuer_credentials|True|
    # update subset of values
    Then innkeeper can update "alice" permissions
    |name|value|
    |endorser_approval|False|
    |store_issuer_credentials|False|
    And innkeeper can get "alice" permissions
    |name|value|
    |endorser_approval|False|
    |create_schema_templates|True|
    |create_credential_templates|True|
    |issue_credentials|True|
    |store_messages|True|
    |store_issuer_credentials|False|
    # update a single value
    Then innkeeper can update "alice" permissions
    |name|value|
    |create_credential_templates|False|
    And innkeeper can get "alice" permissions
    |name|value|
    |endorser_approval|False|
    |create_schema_templates|True|
    |create_credential_templates|False|
    |issue_credentials|True|
    |store_messages|True|
    |store_issuer_credentials|False|

