<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from "vue";
import { useChartStore } from "@/stores/chartStore";
import ChartCard from "@/components/chart/ChartCard.vue";
import InputText from "primevue/inputtext";
import Skeleton from "primevue/skeleton";
import { useAudio } from "@/composables/useAudio";
import Fuse from "fuse.js";
import type { Song } from "@/utils/types";

const chartStore = useChartStore();

// Audio management via composable
const { playingTrackId, volume, setupAudioContext, playPreview, getAudioInfo } =
  useAudio();

// Card state
const flippedCards = ref<Record<number, boolean>>({});
const favoriteTracks = ref<Record<number, boolean>>({});

// Card display management
const maxCardHeight = ref(0);

// Filter and search
const searchQuery = ref("");
const fuse = ref<Fuse<Song> | null>(null);

// Update Fuse instance when chart data changes
watch(
  () => chartStore.chartData,
  () => {
    if (chartStore.chartData?.songs) {
      fuse.value = new Fuse(chartStore.chartData.songs, {
        keys: ["name", "artist"],
        threshold: 0.1, // Lower value = stricter matching
        distance: 100,
        minMatchCharLength: 2,
        shouldSort: true, // Sort by relevance
      });
    } else {
      fuse.value = null;
    }
  },
  { immediate: true }
);

// Computed for filtered songs based on search query
const filteredSongs = computed(() => {
  if (!chartStore.chartData?.songs || !searchQuery.value.trim()) {
    return chartStore.chartData?.songs || [];
  }

  // Use Fuse.js for fuzzy searching
  if (fuse.value) {
    const results = fuse.value.search(searchQuery.value.trim());
    // Sort results by chart position after fuzzy search
    return results
      .map((result) => result.item)
      .sort((a, b) => a.position - b.position);
  }

  // Return empty array if Fuse isn't initialized (should not happen in practice)
  return [];
});

// Watch for chart data changes and update card heights
watch(
  () => chartStore.chartData,
  async () => {
    if (chartStore.chartData) {
      await nextTick();
      // Allow time for images to load
      setTimeout(updateCardHeights, 100);
    }
  },
  { immediate: true }
);

// Reset flipped cards when chart changes
watch([() => chartStore.chartId, () => chartStore.selectedDate], () => {
  flippedCards.value = {};
});

// Setup event listeners and audio context
onMounted(() => {
  window.addEventListener("resize", updateCardHeights);
  setupAudioContext();
});

// Clean up resources
onUnmounted(() => {
  window.removeEventListener("resize", updateCardHeights);
});

// Update card heights for consistent layout
function updateCardHeights() {
  maxCardHeight.value = 0;

  nextTick(() => {
    const cardElements = document.querySelectorAll(".card-front");
    cardElements.forEach((card) => {
      const height = card.scrollHeight;
      if (height > maxCardHeight.value) {
        maxCardHeight.value = height;
      }
    });
  });
}

// Toggle card flip state
function toggleFlip(position: number) {
  flippedCards.value[position] = !flippedCards.value[position];
}

// Toggle favorite status
function toggleFavorite(position: number) {
  favoriteTracks.value[position] = !favoriteTracks.value[position];
}

// Handle volume change
function handleVolumeChange(newVolume: number) {
  volume.value = newVolume;
}
</script>

<template>
  <div class="chart-container h-full w-full">
    <div class="chart-view w-full">
      <!-- Chart Header - Skeleton when loading basic data -->
      <div
        v-if="chartStore.isLoadingBasic || !chartStore.chartData"
        class="chart-view__chart-header p-6 flex flex-col items-center gap-2 mb-6 bg-gradient-to-r from-indigo-700 to-purple-700 text-white rounded-lg"
      >
        <Skeleton width="300px" height="36px" />
        <Skeleton width="80%" height="20px" class="mt-1" />
        <Skeleton width="140px" height="24px" class="mt-2" />
      </div>

      <!-- Chart Header - Actual content when basic data is loaded -->
      <div
        v-else
        class="chart-view__chart-header p-6 flex flex-col items-center gap-2 mb-6 bg-gradient-to-r from-indigo-700 to-purple-700 text-white rounded-lg"
      >
        <h1 class="text-3xl font-bold">{{ chartStore.chartData.title }}</h1>
        <p
          class="chart-view__chart-header__chart-info text-sm text-center max-w-3xl"
        >
          {{ chartStore.chartData.info }}
        </p>
        <p
          class="chart-view__chart-header__chart-week font-medium mt-2 bg-white/20 px-4 py-1 rounded-full"
        >
          {{ chartStore.chartData.week }}
        </p>
      </div>

      <div
        class="chart-controls mb-6 flex flex-col sm:flex-row gap-3 items-start sm:items-center"
      >
        <!-- Search Box -->
        <div class="search-box flex-grow w-full">
          <span class="p-input-icon-left w-full relative">
            <i
              class="pi pi-search absolute left-3 top-1/2 transform -translate-y-1/2 z-10 text-gray-500"
            />
            <InputText
              v-model="searchQuery"
              placeholder="Search songs or artists"
              class="w-full pl-10"
              :disabled="chartStore.isLoadingBasic || !chartStore.chartData"
            />
          </span>
        </div>
      </div>

      <!-- Cards Grid View -->
      <div class="flex flex-wrap gap-4 justify-center">
        <!-- Basic Skeleton Loading: Shown when no data is available -->
        <div
          v-if="chartStore.isLoadingBasic || !chartStore.chartData"
          v-for="n in 12"
          :key="`skeleton-${n}`"
          class="chart-card-container w-full sm:w-[calc(50%-1rem)] md:w-[calc(33.333%-1rem)] lg:w-[calc(25%-1rem)] xl:w-[calc(25%-1rem)]"
        >
          <ChartCard
            :song="{
              position: n,
              name: '',
              artist: '',
              image: '',
              last_week_position: 0,
              peak_position: 0,
              weeks_on_chart: 0,
              url: '',
            }"
            :flipped="false"
            :playing-track-id="null"
            :audio-info="{ progress: 0 }"
            :loading="true"
          />
        </div>

        <!-- Card View: Either default or enriched -->
        <div
          v-else
          v-for="song in filteredSongs"
          :key="`card-${song.position}-${chartStore.chartId}-${chartStore.selectedDate}`"
          class="chart-card-container w-full sm:w-[calc(50%-1rem)] md:w-[calc(33.333%-1rem)] lg:w-[calc(25%-1rem)] xl:w-[calc(25%-1rem)]"
        >
          <!-- Normal cards if we have basic data -->
          <ChartCard
            :song="song"
            :flipped="flippedCards[song.position] || false"
            :playing-track-id="playingTrackId"
            :audio-info="getAudioInfo(song.position)"
            :loading="!chartStore.hasEnrichedData"
            @flip="toggleFlip"
            @favorite="toggleFavorite"
            @play="playPreview"
            @volume-change="handleVolumeChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chart-card-container {
  position: relative;
  perspective: 1500px;
  display: flex;
}
</style>
