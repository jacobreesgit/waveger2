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
  <div class="chart h-full w-full">
    <LoadingSpinner
      v-if="chartStore.isLoading"
      label="Loading chart data..."
    ></LoadingSpinner>

    {{ chartStore }}
  </div>
</template>

<style lang="scss" scoped>
.chart-card {
  transition: all 0.2s ease-in-out;
  height: 100%;

  &:hover {
    transform: translateY(-5px);
  }
}
</style>
