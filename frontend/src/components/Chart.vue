<script setup lang="ts">
import { ref } from "vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import { useChartStore } from "@/stores/chartStore";

const chartStore = useChartStore();

const currentAudio = ref<HTMLAudioElement | null>(null);
const playingTrackId = ref<number | null>(null);

// Play preview if available
function playPreview(previewUrl: string | null, position: number) {
  // Stop any currently playing audio
  if (currentAudio.value) {
    currentAudio.value.pause();
    currentAudio.value = null;

    // If clicking on the same track, just stop it
    if (playingTrackId.value === position) {
      playingTrackId.value = null;
      return;
    }
  }

  if (previewUrl) {
    const audio = new Audio(previewUrl);
    audio.play();
    currentAudio.value = audio;
    playingTrackId.value = position;

    // Reset when playback ends
    audio.onended = () => {
      playingTrackId.value = null;
      currentAudio.value = null;
    };
  }
}

function formatPositionChange(
  current: number,
  last: number | undefined
): string {
  if (last === undefined || last === 0) return "NEW";

  const diff = last - current;
  if (diff === 0) return "=";
  return diff > 0 ? `↑${diff}` : `↓${Math.abs(diff)}`;
}

function getPositionChangeClass(
  current: number,
  last: number | undefined
): string {
  if (last === undefined || last === 0) return "text-blue-500";

  const diff = last - current;
  if (diff === 0) return "text-gray-500";
  return diff > 0 ? "text-green-500" : "text-red-500";
}
</script>

<template>
  <div class="chart h-full">
    <!-- <h1>Chart Component</h1> -->

    <LoadingSpinner
      v-if="chartStore.isLoading"
      label="Loading chart data..."
    ></LoadingSpinner>

    <div
      v-if="chartStore.chartData"
      class="chart-view__chart-header p-6 flex flex-col items-center gap-2"
      :class="{ 'opacity-25': chartStore.isLoading }"
    >
      <h1 class="text-3xl font-bold">{{ chartStore.chartData.title }}</h1>
      <p class="chart-view__chart-header__chart-info text-sm text-center">
        {{ chartStore.chartData.info }}
      </p>
      <p class="chart-view__chart-header__chart-week font-medium">
        {{ chartStore.chartData.week }}
      </p>
    </div>

    {{ chartStore.chartData }}
  </div>
</template>
