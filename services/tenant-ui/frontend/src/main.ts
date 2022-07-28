import router from './router'
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import axios from 'axios';

/*
  UI framework PrimeVue
  https://www.primefaces.org/primevue/
  Each component is defined here so
  the tree shaking can be applied.

  There are material themes available that would
  match the Gov't style.
*/
import PrimeVue from 'primevue/config';
import "primevue/resources/themes/nova-vue/theme.css";
import "primevue/resources/primevue.min.css";
import "primeicons/primeicons.css";
import Toast, { PluginOptions } from "vue-toastification";
import "vue-toastification/dist/index.css";
const options: PluginOptions = {};

loadConfig();

/**
 * @function loadConfig
 * Acquires the configuration state from the backend server
 */
async function loadConfig() {
    // App publicPath is ./ - so use relative path here, will hit the backend server using relative path to root.
    // const configUrl = process.env.NODE_ENV === 'production' ? 'config' : '/app/config';
    // Still need?? tbd

    const storageKey: string = 'config';
    try {
        // Get configuration if it isn't already in session storage
        if (sessionStorage.getItem(storageKey) === null) {
            const { data } = await axios.get('config');
            sessionStorage.setItem(storageKey, JSON.stringify(data));
        }

        // Pass this config over to the app init so it can use provide/inject
        const config = JSON.parse(sessionStorage.getItem(storageKey) || '{}');

        if (!config) {
            throw new Error('Could not fetch config from server or storage');
        }

        initializeApp(config);
    } catch (err) {
        sessionStorage.removeItem(storageKey);
        throw new Error(`Failed to acquire configuration: ${(err as Error).message}`);
    }
}

/**
* @function initializeApp
* Initializes and mounts the Vue instance
* @param {Object} [config] the config fetched from the API
*/
function initializeApp(config: object) {
    const app = createApp(App);
    app.provide('config', config)
    app.use(PrimeVue);
    app.use(router);
    app.use(Toast, options);

    app.mount('#app')
}