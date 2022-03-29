import { appAxios } from '@/services/interceptors';
import { ApiRoutes } from '@/utils/constants';

export default {

  // -------------------------------------------------------------------------
  // Invitations
  // -------------------------------------------------------------------------
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
  // --------------------------------------------------------------/invitations


  // -------------------------------------------------------------------------
  // Credentials
  // -------------------------------------------------------------------------
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
   * @function requestDegree
   * Create a presentation request for an applicant
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} applicantId The identifier for the applicant
   * @returns {Promise} An axios response
   */
  requestDegree(sandboxId, lobId, applicantId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/applicants/${applicantId}/request-degree`);
  },
  // -------------------------------------------------------------/credentials


  // -------------------------------------------------------------------------
  // Presentation Requests
  // -------------------------------------------------------------------------
  /**
   * @function getPresentationRequests
   * Get the current sandboxes in this instance of the showcase app
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @returns {Promise} An axios response
   */
  getPresentationRequests(sandboxId, lobId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/holder/presentation-requests`);
  },

  /**
   * @function acceptPresentationRequest
   * Get the current sandboxes in this instance of the showcase app
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} pres_req_id The identifier for the credential offer
   * @returns {Promise} An axios response
   */
  acceptPresentationRequest(sandboxId, lobId, pres_req_id) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/holder/presentation-requests/${pres_req_id}/accept`);
  },

  /**
   * @function rejectPresentationRequest
   * Get the current sandboxes in this instance of the showcase app
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} pres_req_id The identifier for the credential offer
   * @returns {Promise} An axios response
   */
  rejectPresentationRequest(sandboxId, lobId, pres_req_id) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/holder/presentation-requests/${pres_req_id}/reject`);
  },
  // -------------------------------------------------------------/presentation-requests

  // -------------------------------------------------------------------------
  // Issue
  // -------------------------------------------------------------------------
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
  /**
   * @function issueDegree
   * Issue a degree to a student
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} studentId The identifier for the student
   * @returns {Promise} An axios response
   */
  issueDegree(sandboxId, lobId, studentId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/students/${studentId}/issue-degree`);
  },
  /**
   * @function issueDegree
   * Create a invitation
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @returns {Promise} An axios response
   */
  getIssuedCredentials(sandboxId, lobId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/issued-credentials`);
  },
  /**
   * @function revokeDegree
   * Revoke a degree from a student
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} studentId The identifier for the student
   * @returns {Promise} An axios response
   */
  revokeDegree(sandboxId, lobId, studentId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/students/${studentId}/revoke-degree`);
  },
  // -------------------------------------------------------------/issue


  // -------------------------------------------------------------------------
  // Messages
  // -------------------------------------------------------------------------
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
   * @function updateOutOfBandMessageAction
   * Update the action for an out of band message
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} lobId The identifier for the line of business
   * @param {string} oobId The identifier for the message
   * @param {string} action The action taken on the message
   * @returns {Promise} An axios response
   */
  updateOutOfBandMessageAction(sandboxId, lobId, oobId, action) {
    const payload = {
      id: oobId,
      action: action
    };
    return appAxios().put(`${ApiRoutes.SANDBOXES}/${sandboxId}/lobs/${lobId}/out-of-band-msgs`, payload);
  },
  // -------------------------------------------------------------/messages

};

