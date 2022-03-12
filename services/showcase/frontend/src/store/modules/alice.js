import { showcaseService } from '@/services';
import { NotificationTypes } from '@/utils/constants';

// The store module to hold the "Alice" tenant components
export default {
  namespaced: true,
  state: {
    ofbMessages: [],
    credentials: [],
    credentialOffers: [],
    tenant: {}
  },
  getters: {
    ofbMessages: state => state.ofbMessages,
    credentials: state => state.credentials,
    credentialOffers: state => state.credentialOffers,
    tenant: state => state.tenant
  },
  mutations: {
    SET_OFB_MESSAGES(state, msgs) {
      state.ofbMessages = msgs;
    },
    SET_LOB_CREDENTIALS(state, creds) {
      state.credentials = creds;
    },
    SET_LOB_CREDENTIAL_OFFERS(state, cred_offers) {
      state.credentialOffers = cred_offers;
    },
    SET_TENANT(state, tenant) {
      state.tenant = tenant;
    }
  },
  actions: {
    // Accept an invitation message
    async accept({ dispatch, state, rootState }, msg) {
      try {
        const response = await showcaseService.acceptInvitation(rootState.sandbox.currentSandbox.id, state.tenant.id, msg.sender.id, msg.msg);
        if (response) {
          dispatch('notifications/addNotification', {
            message: `Accepted ${msg.msg_type} from ${msg.sender ? msg.sender.name : ''}`,
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while accepting the invitation.',
          consoleError: `Error accepting invitation: ${error}`,
        }, { root: true });
      }
    },
    // Query the showcase API for out of band messages for this tenant
    async getOfbMessages({ commit, dispatch, state, rootState }) {
      try {
        const response = await showcaseService.getOutOfBandMessages(rootState.sandbox.currentSandbox.id, state.tenant.id);
        commit('SET_OFB_MESSAGES', response.data);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the Out of Band Messages.',
          consoleError: `Error getting messages: ${error}`,
        }, { root: true });
      }
    },
    // Query the showcase API for out of band messages for this tenant
    async getCredentials({ commit, dispatch, state, rootState }) {
      try {
        const response = await showcaseService.getCredentials(rootState.sandbox.currentSandbox.id, state.tenant.id);
        commit('SET_LOB_CREDENTIALS', response.data);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching Credentials.',
          consoleError: `Error getting credentials: ${error}`,
        }, { root: true });
      }
    },
    async getCredentialOffers({ commit, dispatch, state, rootState }) {
      try {
        const response = await showcaseService.getCredentialOffers(rootState.sandbox.currentSandbox.id, state.tenant.id);
        commit('SET_LOB_CREDENTIAL_OFFERS', response.data);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching Credential Offers.',
          consoleError: `Error getting credential offers: ${error}`,
        }, { root: true });
      }
    },
    async acceptCredentialOffer({ dispatch, state, rootState }, cred_issue_id) {
      try {
        await showcaseService.acceptCredentialOffer(rootState.sandbox.currentSandbox.id, state.tenant.id, cred_issue_id);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while accepting Credential Offer.',
          consoleError: `Error getting credential offers: ${error}`,
        }, { root: true });
      }
    },
    async rejectCredentialOffer({ dispatch, state, rootState }, cred_issue_id) {
      try {
        await showcaseService.rejectCredentialOffer(rootState.sandbox.currentSandbox.id, state.tenant.id, cred_issue_id);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while reject Credential Offer.',
          consoleError: `Error getting credential offers: ${error}`,
        }, { root: true });
      }
    },
  }
};
