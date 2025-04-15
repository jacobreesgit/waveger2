<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import Menubar from "primevue/menubar";
import type { MenuItem } from "primevue/menuitem";

const router = useRouter();

const menuItems = computed<MenuItem[]>(() => {
  const currentRouteName = router.currentRoute.value.name;

  return router.options.routes
    .filter((route) => route.meta?.showInNav)
    .map((route) => ({
      label: route.meta?.title as string,
      icon: route.meta?.icon as string,
      class: route.name === currentRouteName ? "active-route" : "",
      command: () => {
        router.push({ name: route.name as string });
      },
    }));
});
</script>

<template>
  <div
    class="nav flex items-center p-2 px-4 pl-0 sm:pl-4 bg-gray-100 relative gap-7"
  >
    <div
      class="nav__logo sm:order-0 order-1 flex-grow sm:flex-grow-0 mr-4 sm:mr-0"
    >
      <RouterLink
        to="/"
        class="nav__logo__logo-link no-underline text-black font-bold text-xl"
        >Waveger</RouterLink
      >
    </div>

    <Menubar
      :model="menuItems"
      class="nav__nav-menu sm:flex-grow bg-transparent border-none sm:order-1 order-0"
    />
  </div>
</template>

<style lang="scss" scoped>
.nav {
  &__nav-menu {
    background: transparent;
    border: none;
  }
}
</style>
