import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import HomeView from "@/views/HomeView.vue";
import ChartView from "@/views/ChartView.vue";
import PredictionView from "@/views/PredictionView.vue";
import LeaderboardView from "@/views/LeaderboardView.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import ProfileView from "@/views/ProfileView.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "Home",
      icon: "pi pi-home",
      showInNav: false,
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
    path: "/predictions",
    name: "predictions",
    component: PredictionView,
    meta: {
      title: "Predictions",
      icon: "pi pi-calendar",
      showInNav: true,
    },
  },
  {
    path: "/leaderboard",
    name: "leaderboard",
    component: LeaderboardView,
    meta: {
      title: "Leaderboard",
      icon: "pi pi-list",
      showInNav: true,
    },
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: {
      title: "Login",
      icon: "pi pi-sign-in",
      showInNav: true,
    },
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
    meta: {
      title: "Register",
      icon: "pi pi-user-plus",
      showInNav: false,
    },
  },
  {
    path: "/profile",
    component: ProfileView,
    meta: {
      title: "Profile",
      icon: "pi pi-user",
      showInNav: false,
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
