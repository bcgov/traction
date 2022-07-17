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
        # this loads data into context.config
        And "alice" will accept credential_offer from "faber"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder credential with status "Accepted"
        And "faber" will have an "Issued" issuer credential

    Scenario: holder can find credentials for holder presentation
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        Then "alice" can find 1 credential(s) for holder presentation

    Scenario: holder will accept a request
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        And "alice" can find 1 credential(s) for holder presentation
        Then "alice" will send presentation from request for "useless-schema"
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | my ext ref id |
        | tags | my,request |
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder presentation with status "Presentation Received"
        And "faber" has a "verified" verifier presentation
        And "alice" can get holder presentation by holder_presentation_id

    Scenario: holder will reject a request
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        Then "alice" will reject presentation from "faber"
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | my ext ref id |
        | tags | my,request |
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder presentation with status "Rejected"
        And "faber" has a "rejected" verifier presentation


    Scenario: holder can update holder presentation metadata
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        Then "alice" can update holder presentation
        | attribute  | value    |
        | alias | new faber |
        | external_reference_id | new ext ref id |
        | tags | updated |
        And "alice" can find holder presentation by tags "updated"
        And "alice" can find holder presentation by alias "new faber"

    Scenario: holder can delete holder presentation metadata
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        Then "alice" can update holder presentation
        | attribute  | value    |
        | alias | faber |
        | external_reference_id | ext ref id |
        | tags | my,request |
        Then "alice" can soft delete holder presentation
        And "alice" cannot find holder presentation by alias "faber"
        And "alice" cannot get holder presentation by holder_presentation_id
        But "alice" can find holder presentation by alias "faber" with deleted flag
        And "alice" can get holder presentation with deleted flag

    Scenario: holder can only send or reject an requested presentation
        When "faber" requests proof of keys in schema "useless-schema" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        And "alice" can find 1 credential(s) for holder presentation
        Then "alice" will send presentation from request for "useless-schema"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder presentation with status "Presentation Received"
        And "faber" has a "verified" verifier presentation
        And "alice" cannot reject an sent presentation
        And "alice" cannot send an sent presentation
