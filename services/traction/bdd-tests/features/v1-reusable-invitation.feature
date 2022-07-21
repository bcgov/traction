Feature: multi-use-invitation   
    Scenario: One invitation used multiple times
        Given we have authenticated at the innkeeper
        And we have "3" traction tenants
        | name  | role    |
        | alice | inviter |
        | faber | invitee1 |
        | bob |  invitee2|
        And "alice" creates a multi-use invitation
        When "faber" receives the invitation from "alice"
        And "bob" receives the invitation from "alice"
        Then "faber" has a connection to "alice" in status "Active"
        And "alice" has a connection to "faber" in status "Active"
        And "bob" has a connection to "alice" in status "Active"
        And "alice" has a connection to "bob" in status "Active"
