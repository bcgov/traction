import { createApp } from "vue";
import App from "./App.vue";
const app = createApp(App);
app.mount("#app");

/*
  UI framework PrimeVue
  https://www.primefaces.org/primevue/
  Each component is defined here so
  the tree shaking can be applied.

  There are material themes available that would
  match the Gov't style.
*/
import PrimeVue from "primevue/config";
import "primevue/resources/themes/nova-vue/theme.css";
import "primevue/resources/primevue.min.css";
import "primeicons/primeicons.css";
app.use(PrimeVue); // Load the UI framework

import Toast, {PluginOptions} from "vue-toastification";
import "vue-toastification/dist/index.css";
const options: PluginOptions = {};
app.use(Toast, options);

