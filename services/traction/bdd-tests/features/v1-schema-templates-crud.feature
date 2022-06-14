Feature: schema templates crud functionality
    Background: two tenants one issuer, one non-issuer to manage schema templates
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | faber | issuer |
        | alice | holder |
        And "faber" is an issuer

    Scenario: issuer can create a schema template
        Given "faber" creates schema template(s)
        | name  | version | attributes | tag | revocation_enabled |
        | bdd-schema | 0.0 | first,last |    | 0                  |
        | bdd-schema-with-cred | 0.0 | first,last | default    | 1                  |
        Then "faber" will have 2 schema template(s)
        And "faber" will have 1 credential template(s)

    Scenario: issuer cannot create a bad schema template
        Given "faber" creates schema template(s)
        | name  | version | attributes | tag | revocation_enabled |
        | bdd-schema | bad | first,last |    | 0                  |
        Then "faber" will have 1 schema template(s)
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        And "faber" can get schema template "bdd-schema" with "Error" status

    Scenario: holder cannot create a schema template
        Given "alice" cannot create a schema template
        Then "alice" will have 0 schema template(s)

    Scenario: issuer can update schema template
        Given "faber" creates schema template(s)
        | name  | version | attributes | tag | revocation_enabled |
        | bdd-schema | 0.0 | first,last |    | 0                  |
        Then "faber" will have 1 schema template(s)
        And "faber" can find schema template "bdd-schema" by name
        And "faber" can find schema template "bdd-schema" by schema_id
        And "faber" can get schema template "bdd-schema" by schema_template_id
        And "faber" can update schema template "bdd-schema"
        | attribute  | value    |
        | name | new bdd-schema |
        | tags | my,template |
        And "faber" can find schema template "new bdd-schema" by tags "my,template"


    Scenario: issuer can delete schema template
        Given "faber" creates schema template(s)
        | name  | version | attributes | tag | revocation_enabled |
        | bdd-schema | 0.0 | first,last |    | 0                  |
        Then "faber" will have 1 schema template(s)
        And "faber" can find schema template "bdd-schema" by schema_id
        And "faber" can delete schema template "bdd-schema"
        Then "faber" cannot find schema template "bdd-schema" by schema_id
        And "faber" cannot get schema template "bdd-schema" by schema_template_id
        But "faber" can find schema template "bdd-schema" with deleted flag
        And "faber" can get schema template "bdd-schema" with deleted flag
