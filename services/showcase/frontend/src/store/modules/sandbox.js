import { showcaseService } from '@/services';

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
        await showcaseService.createSandbox(tag);
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
        // const response = await showcaseService.getSandboxes();
        // commit('SET_SANDBOXES', response.data);
        // await showcaseService.getSandboxes();
        commit('SET_SANDBOXES', (JSON.parse(`[
          {
            "tag": "string",
            "id": "cf66569c-541f-4954-aaf1-91bcc9d07b87",
            "created_at": "2022-02-14T05:05:41.406409",
            "updated_at": "2022-02-14T05:05:41.406409",
            "tenants": [
              {
                "name": "Alice",
                "webhook_url": "http://host.docker.internal:5200/api/v1/webhook",
                "sandbox_id": "cf66569c-541f-4954-aaf1-91bcc9d07b87",
                "id": "5a060d39-5a61-42a5-9b39-f31d966033c9",
                "created_at": "2022-02-14T05:05:43.135985",
                "updated_at": "2022-02-14T05:05:43.135985",
                "wallet_id": "2bd87af3-cd66-4fee-ba3c-3605b96cce23",
                "wallet_key": "bdd73aa8-46d1-4646-a9a6-bbe3d54cdd36"
              },
              {
                "name": "Faber",
                "webhook_url": "http://host.docker.internal:5200/api/v1/webhook",
                "sandbox_id": "cf66569c-541f-4954-aaf1-91bcc9d07b87",
                "id": "c5ad839a-9b2d-49a4-89f8-bdd6abf533aa",
                "created_at": "2022-02-14T05:05:44.865820",
                "updated_at": "2022-02-14T05:05:44.865820",
                "wallet_id": "ede643b4-a0b0-4e9f-9d56-3d2fb8bad301",
                "wallet_key": "9779e389-7125-40f0-ba57-524a3fc1f8fa"
              },
              {
                "name": "Acme",
                "webhook_url": "http://host.docker.internal:5200/api/v1/webhook",
                "sandbox_id": "cf66569c-541f-4954-aaf1-91bcc9d07b87",
                "id": "ee8eee31-b1f9-4a47-bd37-247dc1ecb201",
                "created_at": "2022-02-14T05:05:46.984534",
                "updated_at": "2022-02-14T05:05:46.984534",
                "wallet_id": "2f831851-3a5e-4a10-90f1-9a1451786089",
                "wallet_key": "f318645f-0f32-4d49-9b44-16b57b2eb72e"
              }
            ],
            "students": [
              {
                "name": "Alice",
                "sandbox_id": "cf66569c-541f-4954-aaf1-91bcc9d07b87",
                "id": "9cf9dfc5-33d0-46ca-a99a-ea67194afc49",
                "created_at": "2022-02-14T05:05:47.000653",
                "updated_at": "2022-02-14T05:05:47.000653"
              }
            ]
          }
        ]`)));
      } catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the current sandboxes.',
          consoleError: `Error getting sandboxes: ${error}`,
        }, { root: true });
      }
    },
  }
};
