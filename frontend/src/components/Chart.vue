<script setup lang="ts">
import { ref } from "vue";
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
  <div class="chart">
    <h1>Chart Component</h1>
    <!-- Loading state -->
    <div v-if="chartStore.isLoading" class="text-center py-8">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
      ></div>
      <p class="mt-4">Loading chart data...</p>
    </div>

    <!-- Error state -->
    <div
      v-else-if="chartStore.error"
      class="bg-red-100 p-4 rounded-lg text-red-800"
    >
      <p class="font-semibold">Error loading chart</p>
      <p>{{ chartStore.error }}</p>
    </div>

    <!-- Chart data -->
    <div v-else-if="chartStore.chartData" class="space-y-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">
          {{ chartStore.chartData.title }}
        </h1>
        <p class="text-gray-500">
          {{ chartStore.chartData.week }}
        </p>
      </div>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <!-- Header -->
        <div
          class="bg-gray-100 p-4 grid grid-cols-12 text-sm font-semibold text-gray-700"
        >
          <div class="col-span-1 text-center">#</div>
          <div class="col-span-1 text-center">LAST</div>
          <div class="col-span-7">TITLE</div>
          <div class="col-span-2">PEAK</div>
          <div class="col-span-1 text-center">WEEKS</div>
        </div>

        <div
          v-for="song in chartStore.chartData.songs"
          :key="song.position"
          class="border-b p-4 grid grid-cols-12 items-center hover:bg-gray-50"
        >
          <!-- Position -->
          <div class="col-span-1 text-center font-bold text-xl">
            {{ song.position }}
          </div>

          <!-- Last Week -->
          <div class="col-span-1 text-center">
            <span
              :class="
                getPositionChangeClass(song.position, song.last_week_position)
              "
            >
              {{ formatPositionChange(song.position, song.last_week_position) }}
            </span>
          </div>

          <!-- Song info with artwork -->
          <div class="col-span-7 flex items-center">
            <div class="w-12 h-12 flex-shrink-0 mr-3">
              <img
                :src="song.apple_music?.artwork_url || song.image"
                :alt="song.name"
                class="w-full h-full object-cover rounded"
              />
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-900 truncate">
                {{ song.name }}
              </h3>
              <p class="text-gray-600 truncate">{{ song.artist }}</p>

              <!-- Apple Music Link -->
              <a
                v-if="song.apple_music?.url"
                :href="song.apple_music.url"
                target="_blank"
                class="text-xs text-blue-600 hover:underline inline-flex items-center mt-1"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-3 w-3 mr-1"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"
                  />
                  <path
                    d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"
                  />
                </svg>
                Apple Music
              </a>
            </div>

            <!-- Preview button -->
            <button
              v-if="song.apple_music?.preview_url"
              @click="playPreview(song.apple_music.preview_url, song.position)"
              class="p-2 rounded-full ml-2 hover:bg-gray-200"
              :class="
                playingTrackId === song.position
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100'
              "
              title="Play 30-second preview"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
                v-if="playingTrackId !== song.position"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                  clip-rule="evenodd"
                />
              </svg>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
                v-else
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>

          <!-- Peak position -->
          <div class="col-span-2 text-gray-600">
            <div class="flex items-center">
              <span class="font-medium">Peak: {{ song.peak_position }}</span>
            </div>
          </div>

          <!-- Weeks on chart -->
          <div class="col-span-1 text-center text-gray-600">
            {{ song.weeks_on_chart }}
          </div>
        </div>
      </div>
    </div>

    <!-- No data state -->
    <div v-else class="text-center py-8 text-gray-500">
      No chart data available
    </div>
  </div>
</template>
