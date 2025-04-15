import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "@/router/index";
import "@/style.css";
import App from "@/App.vue";

import PrimeVue from "primevue/config";
import CustomPreset from "@/theme/customPreset";

import ToastService from "primevue/toastservice";

import "primeicons/primeicons.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: CustomPreset,
  },
});
app.use(ToastService);
app.mount("#app");
