Feature: verfication of ARIES presentations
    Background: two tenants are connected, and one has a VC 
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        # verifier will also be the issuer
        | name  | role    |
        | alice | verifier | 
        | faber | prover |
        And "alice" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" and "faber" are connected
        And issuer creates new schema(s) and cred def(s)
        |issuer|schema_name|attrs|cred_def_tag|rev_reg_size|
        |alice|useless-schema|name,title|test|0|
        And check "alice" for 120 seconds for a status of "Active" for "useless-schema"
        And "alice" issues "faber" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" will have a credential_offer from "alice"
        # this loads data into context.config
        And "faber" will accept credential_offer from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a credential
        And "alice" will have an "Issued" issuer credential

    Scenario: alice can make present-proof request
        When "alice" requests proof of keys in schema "useless-schema" from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a present-proof request for "useless-schema"


    Scenario: faber can respond to a present_proof request
        When "alice" requests proof of keys in schema "useless-schema" from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" will have a present-proof request for "useless-schema"
        And "faber" will have credentials to satisfy the present-proof request for "useless-schema"