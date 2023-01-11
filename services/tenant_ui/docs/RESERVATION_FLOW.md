# Tenant Reservation Flow

From the Traction Tenant UI landing page, users can request to create a new tenant.

1. User fills out tenant creation request form:
    1. User provides a valid email address
    1. User provides their full name
    1. User provides their phone/mobile number
    1. User creates a requested tenant name
    1. User provides a reason for the tenant
    1. User is asked to confirm they agree to the terms of service (TODO: Links to the relevant governance documentation or terms and conditions)

1. Traction sends tenant request information to an administrator (Innkeeper):
    1. Information includes all details provided by user

1. Traction automatically sends a confirmation email to the user:
    1. Email contains a link to check status of their reservation (tenant creation)

1. User clicks the "Check Status" link in the confirmation email:
    1. User is taken to a page to check status of their reservation (tenant creation)

1. User Check Status page:
    1. User is asked to enter their email address and reservation password (If link from email is used, these values are automatically filled)

1. Administrator (Innkeeper) reviews tenant information by logging into the Innkeeper UI:
    1. Administrator reviews request and verifies it meets the requirements defined in the governance documentation, other steps may be required to verify the request
    1. Administrator decides whether or not to approve the tenant

1. If tenant is approved:
    1. Traction sends a confirmation email to the user
    1. Email contains a link to login to the Tenant UI
    1. User is now able to log in and use the tenant (either front-end UI or API calls)

1. If tenant is not approved:
    1. Administrator enters a reason for rejection
    1. Traction sends a rejection email to the user including reason for rejection
    1. User is not able to use the tenant
