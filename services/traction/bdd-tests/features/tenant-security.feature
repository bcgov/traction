Feature: tenants can only access their data
    Scenario: tenant scoping with lists
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | alice | issuer |
        | faber | holder |
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | charlie | connections/1.0 |
        And "faber" creates invitation(s)
        | alias  | invitation_type    |
        | david | connections/1.0 |
        Then "alice" will have 1 contact(s)
        Then "faber" will have 1 contact(s)


    Scenario: tenant scoping by object id
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
        | name  | role    |
        | alice | issuer |
        | faber | holder |
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | charlie | connections/1.0 |
        And "faber" creates invitation(s)
        | alias  | invitation_type    |
        | david | connections/1.0 |
        Then "alice" cannot NOT get "faber"s contact to "david" by id