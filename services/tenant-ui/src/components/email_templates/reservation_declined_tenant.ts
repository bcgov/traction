export const RESERVATION_DECLINED_TENANT_TEMPLATE = `
<p>
  Hello <%= it.body.contactName _%>,<br />
  Your Reservation Number (<%= it.body.reservationId _%>) has been updated.
</p>
<p>
  Thank you for your interest in joining Traction. We regret to inform you that
  your request has been declined.
</p>
<p>
  Reason for rejection: <br />
  &nbsp; <%= it.body.stateNotes _%>
</p>
<p>
  If you think there has been an error, you can submit a new request here: <%=
  it.body.serverUrl _%>
</p>
<p>
  Please do not forward this email as it containes private information intended
  only for you. Please do not reply to this email.
</p>
<p>
  Best regards <br />
  Traction Team
</p>
`;
