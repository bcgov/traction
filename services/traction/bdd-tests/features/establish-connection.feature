Feature: aries connection
    Scenario: connect two agents
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
         | name  | role    |
         | alice | invitee |
         | faber | inviter |
        When "faber" generates a connection invitation for "alice"
        And "alice" receives the invitation from "faber"
        Then "faber" has a connection to "alice" in status "Active"
        And "alice" has a connection to "faber" in status "Active"

    Scenario: shorthand to connect two agents
        Given we have "2" traction tenants
         | name  | role    |
         | alice | invitee |
         | faber | inviter |
        And "alice" and "faber" are connected
        Then "faber" has a connection to "alice" in status "Active"
