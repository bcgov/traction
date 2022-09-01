import router from './router';
import { createApp } from 'vue';
import './style.css';
import App from './App.vue';

import { createPinia } from 'pinia';
import { useConfigStore } from './store/configStore';

/**
 * For notifications. The one included in PrimeVue is not working.
 */
import Toast, { PluginOptions } from 'vue-toastification';
import 'vue-toastification/dist/index.css';

/*
  UI framework PrimeVue
  https://www.primefaces.org/primevue/
  Each component is defined here so
  the tree shaking can be applied.

  There are material themes available that would
  match the Gov't style.
*/
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';
import 'primevue/resources/themes/nova-vue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

async function loadApp() {
  // 1. create app
  const app = createApp(App);
  // 2. load storage
  const pinia = createPinia();
  app.use(pinia);
  // 3. load configuration from server (and store it!)
  const configStore = useConfigStore();
  // listen for errors loading configuration...
  const unsubscribe = configStore.$onAction(({ name, after, onError }) => {
    if (name == 'load') {
      after((result) => {
        console.log('configuration loaded from server.');
        console.log(result);
      });
      onError((err) => {
        console.error('error loading configuration from server');
        console.error(err);
        throw new Error(
          `Failed to acquire configuration: ${(err as Error).message}`
        );
      });
    }
  });
  await configStore.load();
  // manually remove the listener
  unsubscribe();

  // 4. load/initialize other components
  app.use(PrimeVue);
  app.use(router);
  app.use(ConfirmationService);
  app.directive('tooltip', Tooltip);
  // 5. initialize the toast notification plugin
  const options: PluginOptions = {};
  app.use(Toast, options);
  // 6. mount the configured app!
  app.mount('#app');
}

loadApp();
