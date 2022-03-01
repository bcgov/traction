import Vue from 'vue';
import Vuex from 'vuex';

import alice from '@/store/modules/alice.js';
import faber from '@/store/modules/faber.js';
import notifications from '@/store/modules/notifications.js';
import sandbox from '@/store/modules/sandbox.js';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: { alice, faber, notifications, sandbox },
  state: {},
  mutations: {},
  actions: {}
});
