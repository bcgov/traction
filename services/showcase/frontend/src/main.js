import 'nprogress/nprogress.css';
import '@bcgov/bc-sans/css/BCSans.css';

import App from './App.vue';
import NProgress from 'nprogress';
import Vue from 'vue';
import VueNativeSock from 'vue-native-websocket';

import '@/filters';
import getRouter from '@/router';
import store from '@/store';
import vuetify from './plugins/vuetify';

Vue.config.productionTip = false;

NProgress.configure({ showSpinner: false });
NProgress.start();

// Globally register all components with base in the name
const requireComponent = require.context('@/components', true, /Base[A-Z]\w+\.(vue|js)$/);
requireComponent.keys().forEach(fileName => {
  const componentConfig = requireComponent(fileName);
  const componentName = fileName.split('/').pop().replace(/\.\w+$/, '');
  Vue.component(componentName, componentConfig.default || componentConfig);
});

const socketApi = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`;
Vue.use(VueNativeSock, socketApi, {
  store: store,
  format: 'json',
  reconnection: true,
  passToStoreHandler: function (eventName, event) {
    if (!eventName.startsWith('SOCKET_')) {
      return;
    }
    let message = event;
    let target = eventName.toUpperCase();
    if (target === 'SOCKET_ONMESSAGE' && this.format === 'json' && event.data) {
      message = JSON.parse(event.data);
      target = 'notifications/onNotification';
    }
    this.store.commit(target, message);
  },
});

new Vue({
  router: getRouter('/'),
  store,
  vuetify,
  render: h => h(App),
}).$mount('#app');

NProgress.done();
