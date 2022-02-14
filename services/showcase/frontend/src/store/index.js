import Vue from 'vue';
import Vuex from 'vuex';

import sandbox from '@/store/modules/sandbox.js';
import notifications from '@/store/modules/notifications.js';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: { sandbox, notifications },
  state: {},
  mutations: {},
  actions: {}
});
