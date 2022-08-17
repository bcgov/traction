Feature: innkeeper tenant management
    Scenario: tenant registers a public did
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | issuer |
        Then "alice" has issuer status "N/A"
        And "alice" cannot register as an issuer
        Then "alice" is allowed to be an issuer by the innkeeper
        And "alice" registers as an issuer
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "alice" will have a public did
        And "alice" has issuer status "Active"

    Scenario: innkeeper creates issuer
        Given we have authenticated at the innkeeper
        And innkeeper check-in "faber" with allow_issue_credentials equals "true"
        Then innkeeper can find "1" tenant(s)
        | public_did_status | issuer_status |
        | Approved | Approved |
        And innkeeper can get "faber" by tenant_id
        And "faber" registers as an issuer
        And we sadly wait for 10 seconds because we have not figured out how to listen for events
        Then "faber" will have a public did
        And "faber" has issuer status "Active"
        Then innkeeper can find "1" tenant(s)
        | public_did_status | issuer_status |
        | Public | Active |
