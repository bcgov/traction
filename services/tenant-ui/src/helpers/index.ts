/**
 * @function buildStatusAutofill
 * Format the reservation status return url with autofil params
 * @param {String} value The body from the email endpoint
 * @returns {String} The URL (env/check-status?email=X&id=Y)
 */
export function buildStatusAutofill(requestBody: any) {
  if (requestBody && requestBody.serverUrlStatusRoute) {
    return `${requestBody.serverUrlStatusRoute}?email=${encodeURIComponent(requestBody.contactEmail)}&id=${encodeURIComponent(requestBody.reservationId)}`;
  } else {
    return "";
  }
}
