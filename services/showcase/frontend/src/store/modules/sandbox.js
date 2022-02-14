import { showcaseService } from '@/services';

// The store module to hold the current showcase app "sandbox session"
export default {
  namespaced: true,
  state: {
    sandboxes: []
  },
  getters: {
    sandboxes: state => state.sandboxes,

  },
  mutations: {
    SET_SANDBOXES(state, sandboxes) {
      state.sandboxes = sandboxes;
    },
  },
  actions: {
    // Query the showcase API for current sandbox states
    async getSandboxes({ commit, dispatch }) {
      try {
        // Get the forms based on the user's permissions
        const response = await showcaseService.getSandboxes();
        commit('SET_SANDBOXES', response.data);
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the current sandboxes.',
          consoleError: `Error getting sandboxes: ${error}`,
        }, { root: true });
      }
    },}
};
