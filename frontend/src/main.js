import Vue from "vue";
import App from "./App.vue";
import router from "./router";

import { PiniaVuePlugin, createPinia } from "pinia";

Vue.use(PiniaVuePlugin);

const pinia = createPinia();

new Vue({
  router,
  pinia,
  render: h => h(App)
}).$mount("#app");
