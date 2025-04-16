<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from "vue";
import { useChartStore } from "@/stores/chartStore";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import ChartCard from "@/components/chart/ChartCard.vue";
import InputText from "primevue/inputtext";
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
        threshold: 0.4, // Lower value = stricter matching
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
    return results.map((result) => result.item);
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
    <LoadingSpinner
      v-if="chartStore.isLoading"
      label="Loading chart data..."
    ></LoadingSpinner>

    <div
      v-if="chartStore.chartData"
      class="chart-view w-full"
      :class="{ 'opacity-25': chartStore.isLoading }"
    >
      <!-- Chart Header -->
      <div
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
        <div class="search-box flex-grow">
          <span class="p-input-icon-left w-full relative">
            <i
              class="pi pi-search absolute left-3 top-1/2 transform -translate-y-1/2 z-10 text-gray-500"
            />
            <InputText
              v-model="searchQuery"
              placeholder="Search songs or artists"
              class="w-full pl-10"
            />
          </span>
        </div>
      </div>

      <!-- Cards Grid View -->
      <div class="flex flex-wrap gap-4 justify-center">
        <div
          v-for="song in filteredSongs"
          :key="song.position"
          class="chart-card-container w-full sm:w-[calc(50%-1rem)] md:w-[calc(33.333%-1rem)] lg:w-[calc(25%-1rem)] xl:w-[calc(25%-1rem)]"
        >
          <ChartCard
            :song="song"
            :flipped="flippedCards[song.position] || false"
            :playing-track-id="playingTrackId"
            :audio-info="getAudioInfo(song.position)"
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
/* Flip animation for PrimeVue transition */
.p-flip-enter-active {
  animation: p-flip-in 0.5s;
}
.p-flip-leave-active {
  animation: p-flip-out 0.5s;
}
@keyframes p-flip-in {
  0% {
    transform: rotateY(90deg);
    opacity: 0;
  }
  100% {
    transform: rotateY(0deg);
    opacity: 1;
  }
}
@keyframes p-flip-out {
  0% {
    transform: rotateY(0deg);
    opacity: 1;
  }
  100% {
    transform: rotateY(90deg);
    opacity: 0;
  }
}

.chart-card-container {
  position: relative;
  perspective: 1500px;
  display: flex;
}
</style>
