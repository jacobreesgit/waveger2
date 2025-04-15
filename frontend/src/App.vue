<template>
  <div class="app-container flex flex-col min-h-screen">
    <Nav />
    <main
      class="app-container__main-content flex flex-1 overflow-y-auto justify-center"
    >
      <!-- <LoadingSpinner
        v-if="isInitializing"
        label="Loading application..."
        centerInContainer
        size="large"
        class="app-container__main-content__loading-spinner h-[unset]"
      /> -->
      <RouterView
        class="app-container__main-content__content flex flex-col w-full items-center p-4"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useChartStore } from "@/stores/chartStore";
import { RouterView } from "vue-router";

import Nav from "@/components/Nav.vue";

const chartStore = useChartStore();

onMounted(() => {
  chartStore.fetchChart();
});
</script>

<style lang="scss" scoped></style>
