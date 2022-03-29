import { lobService, sandboxService } from '@/services';
import { Tenants } from '@/utils/constants';
import { NotificationTypes } from '@/utils/constants';

// The store module to hold the current showcase app "sandbox session"
export default {
  namespaced: true,
  state: {
    currentSandbox: null,
    sandboxes: []
  },
  getters: {
    currentSandbox: state => state.currentSandbox,
    sandboxes: state => state.sandboxes,

  },
  mutations: {
    SET_CURRENT(state, currentSandbox) {
      state.currentSandbox = currentSandbox;
    },
    SET_SANDBOXES(state, sandboxes) {
      state.sandboxes = sandboxes;
    },
  },
  actions: {
    // Post a new sandbox
    async createSandbox({ dispatch }, tag) {
      try {
        await sandboxService.createSandbox(tag);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the current sandboxes.',
          consoleError: `Error getting sandboxes: ${error}`,
        }, { root: true });
      }
    },
    // Query the showcase API for current sandbox states
    async getSandboxes({ commit, dispatch }) {
      try {
        // Get the forms based on the user's permissions
        const response = await sandboxService.getSandboxes();
        commit('SET_SANDBOXES', response.data);
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the current sandboxes.',
          consoleError: `Error getting sandboxes: ${error}`,
        }, { root: true });
      }
    },
    // Promote a tenant in the sandbox to an issuer
    async makeIssuer({ dispatch, state }, tenantId) {
      try {
        const response = await lobService.makeIssuer(state.currentSandbox.id, tenantId);
        if (response) {
          dispatch('notifications/addNotification', {
            message: 'The request to make Faber College an Issuer was received. Check back to see once it has processed',
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while promoting this tenant to an issuer.',
          consoleError: `Error promoting to issuer: ${error}`,
        }, { root: true });
      }
    },
    // Select a specific sandbox to use for the current session
    async selectSandbox({ commit, state }, id) {
      const toSelect = state.sandboxes.find(s => s.id == id);
      if (toSelect) {
        commit('SET_CURRENT', toSelect);
        commit('alice/SET_TENANT', toSelect.lobs.find(t => t.name == Tenants.ALICE), { root: true });
        commit('faber/SET_TENANT', toSelect.lobs.find(t => t.name == Tenants.FABER), { root: true });
        commit('acme/SET_TENANT', toSelect.lobs.find(t => t.name == Tenants.ACME), { root: true });
      }
    },
    // Get the currently selected sandbox again
    async refreshCurrentSandbox({ commit, dispatch, getters }) {
      try {
        // Fetch the current sandbox again and re-mutate the lob's store module tenant settings
        const response = await sandboxService.getSandbox(getters.currentSandbox.id);
        commit('SET_CURRENT', response.data);
        commit('alice/SET_TENANT', response.data.lobs.find(t => t.name == Tenants.ALICE), { root: true });
        commit('faber/SET_TENANT', response.data.lobs.find(t => t.name == Tenants.FABER), { root: true });
        commit('acme/SET_TENANT', response.data.lobs.find(t => t.name == Tenants.ACME), { root: true });
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while getting the sandbox.',
          consoleError: `Error getting sandbox ${getters.currentSandbox.id}: ${error}`,
        }, { root: true });
      }
    },
  }
};
