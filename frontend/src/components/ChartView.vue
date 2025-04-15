<script setup lang="ts">
import { onMounted } from "vue";
import { useChartStore } from "../stores/chartStore";

const chartStore = useChartStore();
const chartOptions = [
  { id: "hot-100", name: "Hot 100" },
  { id: "billboard-200", name: "Billboard 200" },
  { id: "artist-100", name: "Artist 100" },
  { id: "streaming-songs", name: "Streaming Songs" },
];

// Fetch chart data when component mounts
onMounted(() => {
  chartStore.fetchChart();
});

// Play preview if available
function playPreview(previewUrl: string | null) {
  if (previewUrl) {
    const audio = new Audio(previewUrl);
    audio.play();
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Chart selector -->
    <div class="mb-6">
      <select
        v-model="chartStore.chartId"
        @change="chartStore.changeChart(chartStore.chartId)"
        class="rounded-lg border shadow-sm p-2"
      >
        <option v-for="chart in chartOptions" :key="chart.id" :value="chart.id">
          {{ chart.name }}
        </option>
      </select>
    </div>

    <!-- Loading state -->
    <div v-if="chartStore.isLoading" class="text-center py-8">
      Loading chart data...
    </div>

    <!-- Error state -->
    <div v-else-if="chartStore.error" class="bg-red-100 p-4 rounded-lg">
      Error: {{ chartStore.error }}
    </div>

    <!-- Chart data -->
    <div v-else-if="chartStore.chartData">
      <h1 class="text-2xl font-bold mb-4">
        {{ chartStore.chartData.chart.name }} -
        {{ chartStore.chartData.chart.date }}
      </h1>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div
          v-for="entry in chartStore.chartData.entries"
          :key="entry.position"
          class="border-b p-4 flex items-center hover:bg-gray-50"
        >
          <!-- Position -->
          <div class="w-10 text-center font-bold">{{ entry.position }}</div>

          <!-- Artwork -->
          <div class="ml-2 w-16 h-16 flex-shrink-0">
            <img
              :src="entry.apple_music?.artwork_url || entry.image"
              :alt="entry.title"
              class="w-full h-full object-cover rounded"
            />
          </div>

          <!-- Song info -->
          <div class="ml-4 flex-1">
            <h3 class="font-medium">{{ entry.title }}</h3>
            <p class="text-gray-600">{{ entry.artist }}</p>
          </div>

          <!-- Preview button -->
          <button
            v-if="entry.apple_music?.preview_url"
            @click="playPreview(entry.apple_music.preview_url)"
            class="p-2 bg-gray-100 rounded-full"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- No data state -->
    <div v-else class="text-center py-8 text-gray-500">
      No chart data available
    </div>
  </div>
</template>
