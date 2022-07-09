Feature: holding credentials

    Background: two tenants, 1 issuer and 1 holder
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | faber | issuer |
        | alice | holder |
        And "faber" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" and "faber" are connected
        And issuer creates new schema(s) and cred def(s)
        |issuer|schema_name|attrs|cred_def_tag|rev_reg_size|
        |faber|useless-schema|name,title|test|0|
        And check "faber" for 120 seconds for a status of "Active" for "useless-schema"

    Scenario: holder will accept an offer
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will accept credential_offer from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential
