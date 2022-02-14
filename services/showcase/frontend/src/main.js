import 'nprogress/nprogress.css';
import '@bcgov/bc-sans/css/BCSans.css';

import App from './App.vue';
import NProgress from 'nprogress';
import Vue from 'vue';

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

new Vue({
  router: getRouter('/'),
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app');

NProgress.done();
