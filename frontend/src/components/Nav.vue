<script setup lang="ts">
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import routerFile from "@/router/index";
import Menubar from "primevue/menubar";

const router = useRouter();
const route = useRoute();
</script>

<template>
  <div
    class="nav-container flex items-center p-2 px-4 pl-0 sm:pl-4 bg-gray-100 relative"
  >
    <div
      class="nav-container__logo sm:order-0 order-1 flex-grow sm:flex-grow-0 mr-4 sm:mr-0"
    >
      <RouterLink
        to="/"
        class="nav-container__logo__logo-link no-underline text-black font-bold text-xl"
        >Waveger</RouterLink
      >
    </div>

    {{ routerFile }}

    <!-- <Menubar
      :model="menuItems"
      class="nav-container__nav-menu sm:flex-grow bg-transparent border-none mr-4 sm:mx-4 sm:order-1 order-0"
    /> -->

    <div class="nav-container__nav-right order-2 sm:order-3">
      <!-- <CountrySelector /> -->
    </div>
  </div>
</template>

<style lang="scss" scoped>
.nav-container {
  &__nav-menu {
    background: transparent;
    border: none;
  }
}
</style>
