import router from './router';
import { createApp } from 'vue';
import App from './App.vue';

import { createPinia } from 'pinia';
import { useConfigStore } from './store/configStore';

/*
  UI framework PrimeVue
  https://www.primefaces.org/primevue/
  Each component is defined here so
  the tree shaking can be applied.
*/
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';
import './assets/style.scss'; // includes '~primevue/resources/themes/nova/theme.css'
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
// https://github.com/Maronato/vue-toastification
import Toast from 'vue-toastification';
import toastOptions from '@/plugins/toasts/vueToastification';
import i18n from '@/plugins/i18n/i18n';

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
    if (name === 'load') {
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

  // Matomo Setup
  const MATOMO_URL: string = configStore.config.frontend.matomoUrl;
  if (MATOMO_URL) {
    import('./matomoSetup')
      .then((m: { setup: (url: string) => void }) => {
        console.log(m.setup(MATOMO_URL));
        console.log('initialized Matomo');
        console.log(`${MATOMO_URL}`);
      })
      .catch((error) => {
        console.error(error);
      });
  } else {
    console.warn('Matomo not configured');
  }

  // 4. load/initialize other components
  app.use(i18n);
  app.use(PrimeVue);
  app.use(router);
  app.use(ConfirmationService);
  app.directive('tooltip', Tooltip);
  // 5. initialize the toast notification plugin
  app.use(Toast, toastOptions);
  // 6. mount the configured app!
  app.mount('#app');
}

loadApp();
