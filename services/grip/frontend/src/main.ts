import { createApp } from "vue";
import App from "./App.vue";
const app = createApp(App);
app.mount("#app");

/*
  UI framework PrimeVue
  https://www.primefaces.org/primevue/
  Each component is defined here so
  the tree shaking can be applied.
*/
import PrimeVue from "primevue/config";
import InputText from "primevue/inputtext";

app.use(PrimeVue); // Load the UI framework
app.component("InputText", InputText); // Load the component
