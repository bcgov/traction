Feature: innkeeper tenant management
    Scenario: tenant registers a public did
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        Then "alice" is not an issuer
        And "alice" cannot register as an issuer
        Then "alice" is allowed to be an issuer by the innkeeper
        And "alice" registers as an issuer
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a public did
        And "alice" is an issuer
