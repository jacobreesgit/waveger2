<script setup lang="ts">
import { ref, watch } from "vue";
import { useChartStore } from "@/stores/chartStore";
import Chart from "@/components/Chart.vue";
import ChartSelector from "@/components/ChartSelector.vue";

const chartStore = useChartStore();
const selectedDate = ref<string>("");

// Watch for changes to selectedDate and update the chart
watch([selectedDate], () => {
  fetchCurrentChart();
});

// Fetch the current chart with options
function fetchCurrentChart() {
  chartStore.fetchChart(chartStore.chartId, selectedDate.value);
}

// Get today's date in YYYY-MM-DD format for max date attribute
function getToday(): string {
  const today = new Date();
  return today.toISOString().split("T")[0];
}
</script>

<template>
  <div class="chart-view flex flex-col gap-6 max-w-[1200px]">
    <div
      class="chart-view__chart-controls flex w-full gap-2 sm:gap-4 flex-wrap sm:flex-nowrap"
    >
      <ChartSelector />
      <div>
        <label
          for="date-picker"
          class="block text-sm font-medium text-gray-700 mb-1"
          >Select Date</label
        >
        <div class="flex">
          <input
            id="date-picker"
            type="date"
            v-model="selectedDate"
            :max="getToday()"
            class="flex-1 rounded-lg border shadow-sm p-2 bg-white text-gray-800"
            placeholder="YYYY-MM-DD"
          />
        </div>
      </div>
    </div>

    <Chart></Chart>
  </div>
</template>

<style lang="scss" scoped></style>
