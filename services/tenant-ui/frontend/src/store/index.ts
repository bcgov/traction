/**
 * All state and related functionality can be defined
 * here for the entire application to access.
 * We are using the Vue3 Composition API as opposed to Vuex or Pinia
 */

import { reactive } from "vue";

const state = reactive({
  token: null, // API Token
  walletInfo: {},
  contacts: {},
  settings: {},
  schemas: {},
});

export default {
  state,
};
