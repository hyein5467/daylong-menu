import Vue from "vue";
import Router from "vue-router";

import LoadingPage from "../views/keywordLoadingPage.vue";
import keywordSelectPage from "../views/keywordSelectPage.vue";
import menuResultPage from "../views/menuResultPage.vue";

Vue.use(Router);

export default new Router({
  mode: "history",  
  routes: [
    {
      path: "/",
      name: "LoadingPage",
      component: LoadingPage
    },
    {
      path: "/select",
      name: "keywordSelectPage",
      component: keywordSelectPage
    },
    {
      path: "/menu-loading",
      name: "MenuLoading",
      component: () => import("../views/menuLoadingPage.vue")
    },
        {
      path: "/result",
      name: "menuResultPage",
      component: menuResultPage
    },

  ]
});
