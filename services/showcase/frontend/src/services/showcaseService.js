import { appAxios } from '@/services/interceptors';
import { ApiRoutes } from '@/utils/constants';

export default {
  /**
   * @function acceptInvitation
   * Accept an invitation
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @returns {Promise} An axios response
   */
  acceptInvitation(sandboxId, lobId, senderId, message) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/accept-invitation`, { sender_id: senderId, invitation: message });
  },

  /**
   * @function createSandbox
   * Create a new sandbox session
   * @param {string} tag A label for the sandbox
   * @returns {Promise} An axios response
   */
  createSandbox(tag) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}`, { tag: tag });
  },

  /**
   * @function createInvitationStudent
   * Create a invitation for a student
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} studentId The identifier for the student
   * @returns {Promise} An axios response
   */
  createInvitationStudent(sandboxId, lobId, studentId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/create-invitation/student`, { student_id: studentId });
  },

  /**
   * @function createInvitationApplicant
   * Create a invitation for an applicant
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} applicantId The identifier for the applicant
   * @returns {Promise} An axios response
   */
  createInvitationApplicant(sandboxId, lobId, applicantId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/create-invitation/applicant`, { applicant_id: applicantId });
  },

  /**
   * @function issueDegree
   * Create a invitation
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @returns {Promise} An axios response
   */
  issueDegree(sandboxId, lobId, studentId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/students/${studentId}/issue-degree`);
  },


  /**
 * @function getOutOfBandMessages
 * Get out of band messages for the tenant
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @returns {Promise} An axios response
 */
  getOutOfBandMessages(sandboxId, lobId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/out-of-band-msgs`);
  },

  /**
 * @function getSandboxes
 * Get the current sandboxes in this instance of the showcase app
 * @returns {Promise} An axios response
 */
  getSandboxes() {
    return appAxios().get(`${ApiRoutes.SANDBOXES}`);
  },

  /**
 * @function getCredentials
 * Get the current sandboxes in this instance of the showcase app
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @returns {Promise} An axios response
 */
  getCredentials(sandboxId, lobId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/credentials`);
  },


  /**
 * @function getCredentialOffers
 * Get the current sandboxes in this instance of the showcase app
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @returns {Promise} An axios response
 */
  getCredentialOffers(sandboxId, lobId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/credential-offer`);
  },


  /**
 * @function acceptCredentialOffer
 * Get the current sandboxes in this instance of the showcase app
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @param {string} cred_issue_id The identifier for the credential offer
 * @returns {Promise} An axios response
 */
  acceptCredentialOffer(sandboxId, lobId, cred_issue_id) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/credential-offer/${cred_issue_id}/accept`);
  },


  /**
 * @function rejectCredentialOffer
 * Get the current sandboxes in this instance of the showcase app
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @param {string} cred_issue_id The identifier for the credential offer
 * @returns {Promise} An axios response
 */
  rejectCredentialOffer(sandboxId, lobId, cred_issue_id) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/credential-offer/${cred_issue_id}/reject`);
  },


  /**
 * @function makeIssuer
 * Make a tenant an issuer
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} lobId The identifier for the line of business
 * @returns {Promise} An axios response
 */
  makeIssuer(sandboxId, lobId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/make-issuer`);
  },
};

