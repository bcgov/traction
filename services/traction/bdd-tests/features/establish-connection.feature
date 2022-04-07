Feature: aries connection
    Scenario: connect two agents
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
         | name  | role    |
         | alice | invitee |
         | faber | inviter |
        When "faber" generates a connection invitation
        And "alice" receives the invitation from "faber"
        Then "faber" has a connection in state "active"
        And "alice" has a connection in state "active"
