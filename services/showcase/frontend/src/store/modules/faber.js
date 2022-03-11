import { showcaseService } from '@/services';

// The store module to hold the "Alice" tenant components
export default {
  namespaced: true,
  state: {
    ofbMessages: [],
    tenant: { }
  },
  getters: {
    ofbMessages: state => state.ofbMessages,
    tenant: state => state.tenant
  },
  mutations: {
    SET_OFB_MESSAGES(state, msgs) {
      state.ofbMessages = msgs;
    },
    SET_TENANT(state, tenant) {
      state.tenant = tenant;
    }
  },
  actions: {
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
  }
};
