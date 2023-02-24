# Email Templates

Emails are sent to possible tenants when they:

1. Request a reservation
1. Get approved as a tenant.
1. Get denied as a tenant.

In addition the Innkeeper receives an email when a tenant:

1. Requests a reservation.

The email templates are located in the `email_templates` directory. The files are written in [EJS](https://ejs.co/), a templating language that is used to generate HTML. The files are then compiled into HTML and sent to the user as required.

In general, HTML intended for email should be written in a very simple and old school way. This is because email clients are very inconsistent in how they render HTML. For example, some email clients will not render CSS at all. For this reason, the email templates are written in a very simple way. The email templates are not intended to be pretty, but rather to be functional.

In the future, if more complex email templates are needed, we may want to consider using a tool like [mjml](https://mjml.io/).] or possible a service such as [Mailchimp](https://mailchimp.com/).
