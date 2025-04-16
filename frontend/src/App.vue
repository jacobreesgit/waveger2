<script setup lang="ts">
import { onMounted } from "vue";
import { useChartStore } from "@/stores/chartStore";
import { RouterView } from "vue-router";
import Nav from "@/components/nav/Nav.vue";
const chartStore = useChartStore();

onMounted(() => {
  chartStore.fetchChart();
});
</script>

<template>
  <div class="app flex flex-col min-h-screen">
    <Nav />
    <main class="app__main-content flex flex-1 overflow-y-auto justify-center">
      <RouterView
        class="app__main-content__content flex flex-col w-full items-center p-4"
      />
    </main>
  </div>
</template>
