/**
 * @function buildStatusAutofill
 * Format the reservation status return url with autofil params
 * @param {String} value The body from the email endpoint
 * @returns {String} The URL (env/check-status?email=X&id=Y)
 */
export function buildStatusAutofill(requestBody: any) {
  if (requestBody && requestBody.serverUrlStatusRoute) {
    return encodeURI(`${requestBody.serverUrlStatusRoute}?email=${requestBody.contactEmail}&id=${requestBody.reservationId}`);
  } else {
    return "";
  }
}
