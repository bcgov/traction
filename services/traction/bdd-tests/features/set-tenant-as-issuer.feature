Feature: innkeeper tenant management
    Scenario: tenant registers a public did
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        When "alice" is allowed to be an issuer by the innkeeper
        And "alice" registers as an issuer
        Then "alice" will have a public did