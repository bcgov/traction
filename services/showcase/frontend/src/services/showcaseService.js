import { appAxios } from '@/services/interceptors';
import { ApiRoutes } from '@/utils/constants';

export default {
  /**
   * @function acceptInvitation
   * Accept an invitation
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} tenantId The identifier for the tenant
   * @returns {Promise} An axios response
   */
  acceptInvitation(sandboxId, tenantId, senderId, message) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/tenants/${tenantId}/accept-invitation`, { sender_id: senderId, invitation: message });
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
   * @function createInvitation
   * Create a invitation
   * @param {string} sandboxId The identifier for the sandbox
   * @param {string} tenantId The identifier for the tenant
   * @returns {Promise} An axios response
   */
  createInvitation(sandboxId, tenantId, studentId) {
    debugger;
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/tenants/${tenantId}/create-invitation/student`, { student_id: studentId });
  },

  /**
 * @function getOutOfBandMessages
 * Get out of band messages for the tenant
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} tenantId The identifier for the tenant
 * @returns {Promise} An axios response
 */
  getOutOfBandMessages(sandboxId, tenantId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/tenants/${tenantId}/out-of-band-msgs`);
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
 * @function makeIssuer
 * Make a tenant an issuer
 * @param {string} sandboxId The identifier for the sandbox
 * @param {string} tenantId The identifier for the tenant
 * @returns {Promise} An axios response
 */
  makeIssuer(sandboxId, tenantId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/tenants/${tenantId}/make-issuer`);
  },
};
