export const RESERVATION_RECIEVED_INNKEEPER_TEMPLATE = `
<p>
  Hello Innkeeper,<br />
  This email is to notify you that we have received a request from <%=
  it.body.contactName _%> &nbsp; (<%= it.body.contactEmail _%>) with reservation
  ID:
  <b><%= it.body.reservationId _%></b>.
</p>
<p>
  Please login to review and take action on the request: <%= it.body.serverUrl
  _%>/innkeeper
</p>
<p>
  Please do not forward this email as it contains private information intended
  only for you. Please do not reply to this email.
</p>
<p>
  Best regards <br />
  Traction Team
</p>
`;
