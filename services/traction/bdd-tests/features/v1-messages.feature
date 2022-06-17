Feature: messaging contacts

    Background: two tenants, connected to each other
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
         | name  | role    |
         | alice | invitee |
         | faber | inviter |
        When "faber" generates a connection invitation for "alice"
        And "alice" receives the invitation from "faber"
        Then "faber" has a connection to "alice" in status "Active"
        And "alice" has a connection to "faber" in status "Active"

    Scenario: send message to contact without auto response
        When "faber" sets configuration auto_respond_messages to "False"
        And "alice" sends "faber" a message with content "hello faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And "alice" can find 0 message(s) as "Recipient" with "faber"
        And "faber" can find 1 message(s) as "Recipient" with "alice"

    Scenario: send message to contact with auto response
        When "faber" sets configuration auto_respond_messages to "True"
        And "alice" sends "faber" a message with content "hello faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And "alice" can find 1 message(s) as "Recipient" with "faber"

    Scenario: send message to contact find, update and delete
        When "alice" sets configuration auto_respond_messages to "False"
        When "faber" sets configuration auto_respond_messages to "False"
        When "alice" sends "faber" a message with content "hello faber"
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "faber" can find 1 message(s) as "Recipient" with "alice"
        And "alice" can get message with "faber" by message_id
        And "alice" can update message with "faber"
        | attribute  | value    |
        | tags | my,message |
        Then "alice" can find 1 message(s) as "Sender" with "faber" and tags "my,message"
        And "alice" can delete message with "faber"
        Then "alice" cannot find message with "faber" by role
        And "alice" cannot get message with "faber"
        But "alice" can find message with "faber" by role with deleted flag
        And "alice" can get message with "faber" with deleted flag