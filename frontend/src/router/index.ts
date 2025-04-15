import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import HomeView from "../views/HomeView.vue";
import ChartView from "../views/ChartView.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "Home",
      icon: "pi pi-home",
      showInNav: true,
    },
  },
  {
    path: "/charts",
    name: "charts",
    component: ChartView,
    meta: {
      title: "Charts",
      icon: "pi pi-chart-bar",
      showInNav: true,
    },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: { name: "home" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
