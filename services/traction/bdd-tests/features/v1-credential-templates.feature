Feature: credential templates crud functionality
    Background: two tenants one issuer, one non-issuer to manage credential templates
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | faber | issuer |
        | alice | holder |
        And "faber" is an issuer
        Given "faber" creates schema template(s)
        | name  | version | attributes | tag | revocation_enabled |
        | bdd-schema | 0.0 | first,last |    | 0                  |
        Then "faber" will have 1 schema template(s)
        And "faber" will have 0 credential template(s)
        And wait 120 seconds until "faber" can create credential template for "bdd-schema"


    Scenario: issuer can create a credential template using schema id
        Given "faber" creates credential template for "bdd-schema" by schema_id
        Then "faber" will have 1 credential template(s)

    Scenario: issuer can create a credential template using schema template id
        Given "faber" creates credential template for "bdd-schema" by schema_template_id
        Then "faber" will have 1 credential template(s)

    Scenario: holder cannot create a credential template
        Given "alice" cannot create a credential template
        Then "alice" will have 0 credential template(s)

    Scenario: issuer can update credential template
        Given "faber" creates credential template for "bdd-schema" by schema_template_id
        Then "faber" will have 1 credential template(s)
        And "faber" can find credential template "bdd-schema" by name
        And "faber" can find credential template "bdd-schema" by cred_def_id
        And "faber" can get credential template "bdd-schema" by credential_template_id
        And "faber" can update credential template "bdd-schema"
        | attribute  | value    |
        | name | new bdd-schema |
        | tags | my,template |
        And "faber" can find credential template "new bdd-schema" by tags "my,template"

    Scenario: issuer can delete credential template
        Given "faber" creates credential template for "bdd-schema" by schema_template_id
        Then "faber" will have 1 credential template(s)
        And "faber" can find credential template "bdd-schema" by cred_def_id
        And "faber" can delete credential template "bdd-schema"
        Then "faber" cannot find credential template "bdd-schema" by cred_def_id
        And "faber" cannot get credential template "bdd-schema" by credential_template_id
        But "faber" can find credential template "bdd-schema" with deleted flag
        And "faber" can get credential template "bdd-schema" with deleted flag
