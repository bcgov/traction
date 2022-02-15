import { appAxios } from '@/services/interceptors';
import { ApiRoutes } from '@/utils/constants';

export default {
  /**
   * @function getSandboxes
   * Get the current sandboxes in this instance of the showcase app
   * @returns {Promise} An axios response
   */
  getSandboxes() {
    return appAxios().get(`${ApiRoutes.SANDBOXES}`);
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
   * @param {string} tag A label for the sandbox
   * @returns {Promise} An axios response
   */
  createInvitation(sandboxId, tenantId, studentId) {
    return appAxios().post(`${ApiRoutes.SANDBOXES}/${sandboxId}/tenants/${tenantId}/create-invitation/student`, { student_id: studentId });
  },
};
