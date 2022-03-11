import { showcaseService } from '@/services';
import { NotificationTypes } from '@/utils/constants';

// The store module to hold the "Acme" tenant components
export default {
  namespaced: true,
  state: {
    selectedApplicant: null,
    tenant: {}
  },
  getters: {
    selectedApplicant: state => state.selectedApplicant,
    tenant: state => state.tenant
  },
  mutations: {
    SET_SELECTED_APPLICANT(state, applicant) {
      state.selectedApplicant = applicant;
    },
    SET_TENANT(state, tenant) {
      state.tenant = tenant;
    }
  },
  actions: {
    // Send an invitation message to the applicant
    async createInvitation({ dispatch, state, rootState }, applicant) {
      try {
        const response = await showcaseService.createInvitationApplicant(rootState.sandbox.currentSandbox.id, state.tenant.id, applicant.id);
        if (response) {
          dispatch('notifications/addNotification', {
            message: `Invited applicant ${applicant.alias} to ACME`,
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while inviting the applicant.',
          consoleError: `Error inviting applicant: ${error}`,
        }, { root: true });
      }
    },
  }
};
