<script setup lang="ts">
import { ref, watch } from "vue";
import { useChartStore } from "@/stores/chartStore";
import Select from "primevue/select";

const store = useChartStore();
const selectedChartId = ref(store.chartId);

const chartOptions = [
  { id: "hot-100", title: "Billboard Hot 100™" },
  { id: "billboard-200", title: "Billboard 200™" },
  { id: "artist-100", title: "Billboard Artist 100" },
  { id: "emerging-artists", title: "Emerging Artists" },
  { id: "streaming-songs", title: "Streaming Songs" },
  { id: "radio-songs", title: "Radio Songs" },
  { id: "digital-song-sales", title: "Digital Song Sales" },
  { id: "summer-songs", title: "Songs of the Summer" },
  { id: "top-album-sales", title: "Top Album Sales" },
  { id: "top-streaming-albums", title: "Top Streaming Albums" },
  { id: "independent-albums", title: "Independent Albums" },
  { id: "vinyl-albums", title: "Vinyl Albums" },
  { id: "indie-store-album-sales", title: "Indie Store Album Sales" },
  {
    id: "billboard-u-s-afrobeats-songs",
    title: "Billboard U.S. Afrobeats Songs",
  },
];

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
      :options="chartOptions"
      optionLabel="title"
      optionValue="id"
      placeholder="Select a chart"
      class="w-full"
      :disabled="store.isLoading"
    />
  </div>
</template>
