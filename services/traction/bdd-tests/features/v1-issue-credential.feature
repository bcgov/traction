Feature: issuing credentials

    Background: two tenants, 1 issuer can write schema and cred_def
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | alice | issuer |
        | faber | holder |
        And "alice" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" and "faber" are connected
        And issuer creates new schema(s) and cred def(s)
        |issuer|schema_name|attrs|cred_def_tag|rev_reg_size|
        |alice|useless-schema|name,title|test|0|
        And check "alice" for 120 seconds for a status of "Active" for "useless-schema"

    Scenario: offer a credential to an active contact
        When "alice" issues "faber" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential_offer from "alice"

    Scenario: holder will accept an offered credential to an active contact
        When "alice" issues "faber" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" will have a credential_offer from "alice"
        # this loads data into context.config
        And "faber" will accept credential_offer from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential
        And "alice" will have an "Issued" issuer credential

    Scenario: issuer will revoke an accepted credential
        Given issuer creates new schema(s) and cred def(s)
        |issuer|schema_name|attrs|cred_def_tag|rev_reg_size|
        |alice|revocable-schema|name,title|test|4|
        And check "alice" for 120 seconds for a status of "Active" for "revocable-schema"
        When "alice" issues "faber" a "revocable-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" will have a credential_offer from "alice"
        # this loads data into context.config
        And "faber" will accept credential_offer from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential
        And "alice" will have an "Issued" issuer credential
        When "alice" revokes credential from "faber"
        Then "alice" will have an "Revoked" issuer credential

    Scenario: issuer can import schema
        Given issuer imports schema(s)
        |issuer|schema_id|name|cred_def_tag|rev_reg_size|
        |alice|9vnQTCy6NQ7mxUVhLtaPZY:2:registration.registries.ca:1.0.42|registration-schema|test|4|
        And check "alice" for 120 seconds for a status of "Active" for "registration-schema"
