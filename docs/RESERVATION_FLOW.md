# Reservation Flow

From the Traction Tenant UI landing page, users can request to create a new tenant.

1. User fills out tenant creation request form:
    1. User provides a valid email address
    1. User provides their full name
    1. User provides their phone/mobile number
    1. User creates a requested tenant name
    1. User provides a reason for the tenant

1. Traction automatically sends a confirmation email to the user:
    1. Email contains a link to confirm their account, including the Reservation ID (a GUID)

1. User clicks the confirmation link:
    1. User is taken to a page to confirm their account

1. User confirmation page:
    1. User is asked to enter their reservation id and password
    1. User is asked to confirm they agree to the terms of service (TODO: Links to the relevant governance documentation or terms and conditions)

1. Traction sends account information to an administrator (Innkeeper):
    1. Information includes username, email address, and password

1. Administrator (Innkeeper) reviews account information:
    1. Administrator decides whether or not to approve the account

1. If account is approved:
    1. Traction sends a confirmation email to the user
    1. User is now able to log in and use the tenant (either front-end UI or API calls)

1. If account is not approved:
    1. Administrator sends a rejection email to the user
    1. User is not able to use the tenant
