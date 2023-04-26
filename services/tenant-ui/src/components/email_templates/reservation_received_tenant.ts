export const RESERVATION_RECIEVED_TENANT_TEMPLATE = `
<p>
  Hello <%= it.body.contactName _%>,<br />Thank you for your request to join
  Traction
</p>
<p>
  This email confirms we have received your request and a Representative is
  working on your case. <br />
  Your Reservation Number is <b><%= it.body.reservationId _%></b>.
</p>
<p>
  A decision on the request usually takes 2-3 days from the date of this email.
  You can verify the status of your request by entering your email and
  Reservation Number here: <a href="<%= it.body.serverUrlStatusRouteAutofill _%>"><%= it.body.serverUrlStatusRoute _%></a>
</p>
<p>
  Please do not forward this email as it contains private information intended
  only for you. Please do not reply to this email.
</p>
<p>Thank you for choosing Traction!</p>
<p>
  Best regards <br />
  Traction Team
</p>
`;
