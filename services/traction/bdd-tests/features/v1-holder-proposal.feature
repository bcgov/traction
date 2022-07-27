Feature: holding presentations

    Background: two tenants, 1 issuer/verifier and 1 holder
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        # verifier will also be the issuer
        | name  | role    |
        | faber | verifier |
        | alice | prover |
        And "faber" is an issuer
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "faber" and "alice" are connected
        And issuer creates new schema(s) and cred def(s)
        |issuer|schema_name|attrs|cred_def_tag|rev_reg_size|
        |faber|useless-schema|name,title|test|0|
        And check "faber" for 120 seconds for a status of "Active" for "useless-schema"
        And "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a credential_offer from "faber"
        And "alice" will accept credential_offer from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        And "faber" will have an "Issued" issuer credential
        And "alice" will have 1 holder credential(s)


    Scenario: holder can propose a presentation to verifier
        When "alice" proposes a presentation to "faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        And "alice" will have 1 holder presentation(s)
        And "alice" can find 1 credential(s) for holder presentation
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder presentation with status "Presentation Received"
        And "faber" has a "verified" verifier presentation
