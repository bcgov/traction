export const RESERVATION_APPROVED_TENANT_TEMPLATE = `
<p>
  Hello <%= it.body.contactName _%>,<br />
  Your Reservation Number (<%= it.body.reservationId _%>) has been updated.
</p>
<p>
  We are pleased to inform you that your reservation request is approved. Here
  is the Reservation Password that is required to validate your account:
  <b><%= it.body.reservationPassword _%></b></p>
<p>
 Please use this link to validate your account:
 <a href="<%= it.body.serverUrlStatusRouteAutofill _%>"><%= it.body.serverUrlStatusRoute _%></a>
</p>
<p>
  After successful validation of your account, a new Wallet ID and Wallet Key
  will be generated. Please save the newly generated Wallet ID and Wallet Key in
  a secure location as we never share this information over email nor do we
  re-issue upon request.
</p>
<p>
  Traction will never contact you to ask for details about your login
  credentials.
</p>
<p>
  Please do not forward this e-mail as it contains private information intended
  only for you. Please do not reply to this e-mail.
</p>
<p>
  Best regards <br />
  Traction Team
</p>
`;
