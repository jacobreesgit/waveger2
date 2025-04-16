<script setup lang="ts">
import { ref, watch } from "vue";
import { useChartStore } from "@/stores/chartStore";
import { CHART_OPTIONS } from "@/utils/chartConstants";
import Select from "primevue/select";

const store = useChartStore();
const selectedChartId = ref(store.chartId);

// Watch for changes to selectedChartId and update the store
watch(selectedChartId, (newChartId) => {
  if (newChartId !== store.chartId) {
    store.changeChart(newChartId);
  }
});

// Keep the local state in sync with the store
watch(
  () => store.chartId,
  (newChartId) => {
    selectedChartId.value = newChartId;
  }
);
</script>

<template>
  <div class="chart-selector grow flex flex-col gap-1">
    <label for="chart-select" class="block text-sm font-medium text-gray-700"
      >Select Chart</label
    >
    <Select
      id="chart-select"
      v-model="selectedChartId"
      :options="CHART_OPTIONS"
      optionLabel="title"
      optionValue="id"
      placeholder="Select a chart"
      class="w-full"
      :disabled="store.isLoading"
    />
  </div>
</template>
