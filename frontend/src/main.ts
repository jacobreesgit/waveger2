import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "@/router/index";
import "@/style.css";
import App from "@/App.vue";

import PrimeVue from "primevue/config";
import CustomPreset from "@/theme/customPreset";
import ToastService from "primevue/toastservice";

import "primeicons/primeicons.css";
import { FontAwesomeIcon } from "@/plugins/fontawesome";

// Create and configure the Vue application
const app = createApp(App);

// Register plugins
app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: CustomPreset,
  },
});
app.use(ToastService);

// Register global components
app.component("font-awesome-icon", FontAwesomeIcon);

// Mount the app
app.mount("#app");
