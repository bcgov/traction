Feature: verifier presentation request templates
    Background: two tenants are connected, and one has a VC 
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


    Scenario: smoke test presentation request templates
        Given "faber" creates presentation request template for "useless-schema"
        | name  | external_reference_id | tags |
        | my_template  | ref id            | template, useless-schema |
        Then "faber" will have 1 presentation request template(s)
        Then "faber" can update presentation request template "my_template"
        | attribute  | value    |
        | name | new my_template |
        | external_reference_id | new ref id |
        | tags | my,new template |
        And "faber" can find presentation request template by tags "my,new template"
        And "faber" can find presentation request template by external reference id "new ref id"
        Then "faber" will reload presentation request template(s)
        And "faber" can get presentation request template "new my_template" by id
        Then "faber" requests proof of keys with template "new my_template" from "alice"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "alice" will have a holder presentation with status "Request Received"
        And "alice" can find 1 credential(s) for holder presentation
        Then "alice" will send presentation from request for "useless-schema"
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a holder presentation with status "Presentation Received"
        And "faber" has a "verified" verifier presentation
        And "alice" can get holder presentation by holder_presentation_id
        Then "faber" can delete presentation request template "new my_template"
        And "faber" cannot find presentation request template by tags "my,new template"
        And "faber" cannot find presentation request template by external reference id "new ref id"
        And "faber" cannot get presentation request template "new my_template" by id
        But "faber" can get presentation request template "new my_template" by id and deleted flag
        And "faber" can find presentation request template "new my_template" by tags "my,new template" and deleted flag
