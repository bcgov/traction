Feature: issuing credentials

    Scenario: An issuer can write a new schema and cred_def
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        And "alice" is an issuer
        When "alice" writes a new schema "useless-schema" and cred def tagged "test"
        |attr|
        |name|
        |title|
        Then "alice" will have a tenant_schema record with an "in_progress" cred_def for "useless-schema"


    # Scenario: Issue a credential to an active contact
    #     Given we have authenticated at the innkeeper
    #     And we have "2" traction tenants
    #     | name  | role    |
    #     | alice | issuer |
    #     | faber | holder |
    #     And "alice" is an issuer
    #     And "alice" and "faber" are connected
    #     And "alice" writes a new schema "useless-schema" and cred def tagged "test"
    #     |attr|
    #     |name|
    #     |title|
    #     And we sadly wait for 10 seconds because we have not figured out how to listen for events
    #     And "alice" has a tenant_schema record with an "completed" cred_def for "useless-schema"

    #     When "alice" issues "faber" a "useless-schema" credential
    #     |attr|
    #     |name|
    #     |title|
    #     Then "faber" will have a credential_offer from "alice"