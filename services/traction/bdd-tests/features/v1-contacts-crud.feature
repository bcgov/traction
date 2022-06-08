Feature: contacts crud functionality
    Background: single authorized tenant to manage their contacts
        Given we have authenticated at the innkeeper
        And we have "1" traction tenants
        | name  | role    |
        | alice | holder |

    Scenario: tenant can create an invitation
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | faber | connections/1.0 |
        | acme | didexchange/1.0 |
        | mercury | connections/1.0 |
        | venus | didexchange/1.0 |
        | earth | connections/1.0 |
        | mars | didexchange/1.0 |
        | jupiter | connections/1.0 |
        | saturn | didexchange/1.0 |
        | uranus | connections/1.0 |
        | neptune | didexchange/1.0 |
        | pluto | connections/1.0 |
        Then "alice" will have 11 contact(s)
        And "alice" can find contact "faber" by alias
        And "alice" will have a next page link in contact list

    Scenario: tenant can update contact information
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | faber | connections/1.0 |
        Then "alice" will have 1 contact(s)
        And "alice" can find contact "faber" by alias
        And "alice" can get contact "faber" by contact_id
        And "alice" can update contact "faber"
        | attribute  | value    |
        | alias | new faber |
        | external_reference_id | new ext ref id |
        | public_did | new public did |
        | tags | my,contact |
        And "alice" can find contact "new faber" by tags "my,contact"

    Scenario: tenant can delete contact
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | faber | connections/1.0 |
        Then "alice" will have 1 contact(s)
        And "alice" can find contact "faber" by alias
        And "alice" can delete contact "faber"
        Then "alice" cannot find contact "faber" by alias
        And "alice" cannot get contact "faber" by contact_id
        But "alice" can find contact "faber" with deleted flag
        And "alice" can get contact "faber" with deleted flag

    Scenario: tenant can get contact with extra attributes
        When "alice" creates invitation(s)
        | alias  | invitation_type    |
        | faber | connections/1.0 |
        Then "alice" will have 1 contact(s)
        And "alice" can get contact "faber" by contact_id
        And "alice" can get contact "faber" with timeline
        And "alice" can get contact "faber" with acapy




