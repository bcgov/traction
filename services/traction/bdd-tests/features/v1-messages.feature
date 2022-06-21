Feature: messaging contacts

    Background: two tenants, connected, can store messages and auto-respond
        Given we have authenticated at the innkeeper
        And we have "2" traction tenants
         | name  | role    |
         | alice | invitee |
         | faber | inviter |
        # to simplify testing, turn on storage of messages as default for each scenario
        # we can flip the tenant flags in the scenario as needed for different behaviour
        And innkeeper sets permissions "store_messages" to "True" for "alice"
        And innkeeper sets permissions "store_messages" to "True" for "faber"
        And "alice" sets configuration "store_messages" to "True"
        And "faber" sets configuration "store_messages" to "True"
        And "alice" sets configuration "auto_respond_messages" to "True"
        And "faber" sets configuration "auto_respond_messages" to "True"
        When "faber" generates a connection invitation for "alice"
        And "alice" receives the invitation from "faber"
        Then "faber" has a connection to "alice" in status "Active"
        And "alice" has a connection to "faber" in status "Active"

    Scenario: send message to contact with auto response
        When "alice" sends "faber" a message with content "hello faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And "alice" can find 1 message(s) as "Recipient" with "faber"

    Scenario: send message to contact without auto response
        When "faber" sets configuration "auto_respond_messages" to "False"
        And "alice" sends "faber" a message with content "hello faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And "alice" can find 0 message(s) as "Recipient" with "faber"
        And "faber" can find 1 message(s) as "Recipient" with "alice"

    Scenario: send messages and check store_messages behavior
        When "faber" sets configuration "auto_respond_messages" to "False"
        And "faber" sets configuration "store_messages" to "False"
        And "alice" sends "faber" a message with content "hello faber"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Sender" with "faber"
        And "alice" can find 0 message(s) as "Recipient" with "faber"
        And "faber" can find 1 message(s) as "Recipient" with "alice"
        And "faber" messages as "Recipient" have no content
        # faber needs to store messages again, so the send (which checks content) will work
        # and alice already has stored_messages = True
        Then "faber" sets configuration "store_messages" to "True"
        And "faber" sends "alice" a message with content "hello alice"
        And we sadly wait for 5 seconds because we have not figured out how to listen for events
        Then "alice" can find 1 message(s) as "Recipient" with "faber"
        And "alice" messages as "Recipient" will have content

    Scenario: send message to contact find, update and delete
        When "alice" sets configuration "auto_respond_messages" to "False"
        When "faber" sets configuration "auto_respond_messages" to "False"
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