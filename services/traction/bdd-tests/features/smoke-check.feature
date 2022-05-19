Feature: check the environment
    Scenario: tenant registers a public did
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        When "alice" calls the hard-delete endpoint
        Then "alice" will not exist