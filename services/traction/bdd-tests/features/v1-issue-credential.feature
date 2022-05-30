Feature: issuing credentials

    Scenario: An issuer can write a new schema and cred_def
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        And "alice" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        When "alice" writes a new schema "useless-schema" and cred def tagged "test"
        |attr|
        |name|
        |title|
        # let schema get signed by endorser, and written to ledger, and cred_def get started
        Then check "alice" for 120 seconds for a cred_def status of "transaction_acked" for "useless-schema"


    Scenario: offer a credential to an active contact
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | alice | issuer |
        | faber | holder |
        And "alice" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" and "faber" are connected
        And "alice" writes a new schema "useless-schema" and cred def tagged "test"
        |attr|
        |name|
        |title|
        And check "alice" for 120 seconds for a cred_def status of "transaction_acked" for "useless-schema"
        When "alice" issues "faber" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential_offer from "alice"


    Scenario: Issue a credential to an active contact
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | alice | issuer |
        | faber | holder |
        And "alice" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" and "faber" are connected
        And "alice" writes a new schema "useless-schema" and cred def tagged "test"
        |attr|
        |name|
        |title|
        And check "alice" for 120 seconds for a cred_def status of "transaction_acked" for "useless-schema"
        # this loads data into context.config
        When "alice" issues "faber" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" will have a credential_offer from "alice"
        # this loads data into context.config
        And "faber" will accept credential_offer from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential
        And "alice" will have an acked credential_offer