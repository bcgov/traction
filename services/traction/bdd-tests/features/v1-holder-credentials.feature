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
        Then "alice" will have a holder credential with status "Accepted"

    Scenario: holder will reject an offer
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will reject credential_offer from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Rejected"
        And "faber" will have an "Offer not Accepted" issuer credential


    Scenario: holder can update holder credential metadata
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will accept credential_offer from "faber"
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | my ext ref id |
        | tags | my,offer |
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        Then "alice" will have 1 holder credential(s)
        And "alice" can find holder credential by alias "faber"
        And "alice" can get holder credential by holder_credential_id
        And "alice" can update holder credential
        | attribute  | value    |
        | alias | new faber |
        | external_reference_id | new ext ref id |
        | tags | updated |
        And "alice" can find holder credential by tags "updated"

    Scenario: holder can delete holder credential metadata
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will accept credential_offer from "faber"
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | my ext ref id |
        | tags | my,offer |
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        And "alice" has 1 credential(s) in wallet
        And "alice" can soft delete holder credential
        Then "alice" cannot find holder credential by alias "faber"
        And "alice" cannot get holder credential by holder_credential_id
        But "alice" can find holder credential by alias "faber" with deleted flag
        And "alice" can get holder credential with deleted flag
        And "alice" has 1 credential(s) in wallet

    Scenario: holder can only accept or reject an offered credential
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will accept credential_offer from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        And "alice" cannot reject an accepted offer
        And "alice" cannot accept an accepted offer

    Scenario: holder can delete holder credential and wallet credential
        When "faber" issues "alice" a "useless-schema" credential
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a credential_offer from "faber"
        Then "alice" will accept credential_offer from "faber"
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | my ext ref id |
        | tags | my,offer |
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        And "alice" has 1 credential(s) in wallet
        Then "alice" can hard delete holder credential
        And "alice" cannot find holder credential by alias "faber" with deleted flag
        And "alice" cannot get holder credential with deleted flag
        And "alice" has 0 credential(s) in wallet
