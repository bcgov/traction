import { appAxios } from '@/services/interceptors';
import { ApiRoutes } from '@/utils/constants';

export default {

  // -------------------------------------------------------------------------
  // Sandbox
  // -------------------------------------------------------------------------
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
   * @function getSandboxes
   * Get the current sandboxes in this instance of the showcase app
   * @returns {Promise} An axios response
   */
  getSandboxes() {
    return appAxios().get(`${ApiRoutes.SANDBOXES}`);
  },

  /**
   * @function getSandbox
   * Get a specific sandbox in this instance of the showcase app
   * @param {string} sandboxId The identifier for the sandbox
   * @returns {Promise} An axios response
   */
  getSandbox(sandboxId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}`);
  },
  // -----------------------------------------------------------------/sandbox


  // -------------------------------------------------------------------------
  // Students
  // -------------------------------------------------------------------------
  /**
   * @function getStudents
   * Get the students list in this sandbox
   * @returns {Promise} An axios response
   */
  getStudents(sandboxId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/students`);
  },
  // -----------------------------------------------------------------/students


  // -------------------------------------------------------------------------
  // Applicants
  // -------------------------------------------------------------------------
  /**
   * @function getApplicants
   * Get the applicants list in this sandbox
   * @returns {Promise} An axios response
   */
  getApplicants(sandboxId) {
    return appAxios().get(`${ApiRoutes.SANDBOXES}/${sandboxId}/applicants`);
  },
  // --------------------------------------------------------------/applicants

};

