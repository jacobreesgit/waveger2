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

    <div
      v-if="chartStore.chartData"
      class="chart-view"
      :class="{ 'opacity-25': chartStore.isLoading }"
    >
      <div
        class="chart-view__chart-header p-6 flex flex-col items-center gap-2 mb-6"
      >
        <h1 class="text-3xl font-bold">{{ chartStore.chartData.title }}</h1>
        <p
          class="chart-view__chart-header__chart-info text-sm text-center max-w-3xl"
        >
          {{ chartStore.chartData.info }}
        </p>
        <p class="chart-view__chart-header__chart-week font-medium mt-2">
          {{ chartStore.chartData.week }}
        </p>
      </div>

      <div class="flex flex-wrap gap-4 justify-center">
        <div
          v-for="(song, index) in chartStore.chartData.songs"
          :key="song.position"
          class="chart-card w-full sm:w-[calc(50%-1rem)] md:w-[calc(33.333%-1rem)] lg:w-[calc(25%-1rem)] xl:w-[calc(25%-1rem)] 2xl:w-[calc(25%-1rem)] flex flex-col bg-white rounded-lg shadow-md overflow-hidden transition-transform duration-200 hover:shadow-lg hover:-translate-y-1"
        >
          <div class="relative">
            <img
              :src="song.apple_music?.artwork_url || song.image"
              :alt="`${song.name} by ${song.artist}`"
              class="w-full aspect-square object-cover"
            />
            <div
              class="absolute top-0 left-0 m-2 bg-black bg-opacity-70 text-white font-bold rounded-full w-10 h-10 flex items-center justify-center"
            >
              {{ song.position }}
            </div>
            <div
              class="absolute bottom-0 right-0 m-2 rounded-full w-10 h-10 flex items-center justify-center bg-black bg-opacity-70 cursor-pointer hover:bg-opacity-90 transition-all"
              @click="playPreview(song.apple_music?.preview_url, song.position)"
              v-if="song.apple_music?.preview_url"
            >
              <span
                v-if="playingTrackId === song.position"
                class="text-white pi pi-pause-circle text-lg"
              ></span>
              <span v-else class="text-white pi pi-play-circle text-lg"></span>
            </div>
          </div>

          <div class="p-4 flex flex-col flex-grow">
            <div class="flex justify-between items-start mb-1">
              <h3 class="font-bold text-lg" :title="song.name">
                {{ song.name }}
              </h3>
              <div
                :class="
                  getPositionChangeClass(song.position, song.last_week_position)
                "
                class="text-sm font-bold ml-2 whitespace-nowrap"
              >
                {{
                  formatPositionChange(song.position, song.last_week_position)
                }}
              </div>
            </div>

            <p class="text-gray-600 mb-2" :title="song.artist">
              {{ song.artist }}
            </p>

            <div
              class="mt-auto pt-3 border-t border-gray-100 text-sm text-gray-500 flex justify-between"
            >
              <div>
                Peak: <span class="font-medium">{{ song.peak_position }}</span>
              </div>
              <div>
                Weeks:
                <span class="font-medium">{{ song.weeks_on_chart }}</span>
              </div>
            </div>
          </div>

          <div class="chart-card__actions p-3 pt-0 flex gap-2">
            <a
              v-if="song.apple_music?.url"
              :href="song.apple_music.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-xs py-1 px-3 bg-black text-white rounded-full flex items-center"
            >
              <i class="pi pi-apple mr-1"></i> Apple Music
            </a>
          </div>
        </div>
      </div>
    </div>
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
