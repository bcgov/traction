import 'nprogress/nprogress.css';
import '@bcgov/bc-sans/css/BCSans.css';

import App from './App.vue';
import NProgress from 'nprogress';
import Vue from 'vue';

import getRouter from '@/router';
import vuetify from './plugins/vuetify';

Vue.config.productionTip = false;

NProgress.configure({ showSpinner: false });
NProgress.start();

new Vue({
  router: getRouter('/'),
  vuetify,
  render: h => h(App)
}).$mount('#app');

NProgress.done();
