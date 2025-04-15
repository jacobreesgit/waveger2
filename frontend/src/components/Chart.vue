<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from "vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import { useChartStore } from "@/stores/chartStore";

const chartStore = useChartStore();

// Audio management
const currentAudio = ref<HTMLAudioElement | null>(null);
const playingTrackId = ref<number | null>(null);
const audioProgress = ref<Record<number, number>>({});
const flippedCards = ref<Record<number, boolean>>({});

// Favorite tracks (no real functionality)
const favoriteTracks = ref<Record<number, boolean>>({});

// Web Audio API components
const audioContext = ref<AudioContext | null>(null);
const analyser = ref<AnalyserNode | null>(null);

// Card height management
const maxCardHeight = ref(0);

// Watch for chart data changes and update card heights
watch(
  () => chartStore.chartData,
  async () => {
    if (chartStore.chartData) {
      // Wait for the DOM to update before measuring
      await nextTick();
      // Set timeout for any image loading
      setTimeout(updateCardHeights, 100);
    }
  },
  { immediate: true }
);

// Update card heights when window is resized
onMounted(() => {
  window.addEventListener("resize", updateCardHeights);
  // Initialize Web Audio API
  try {
    audioContext.value = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    analyser.value = audioContext.value.createAnalyser();
    analyser.value.connect(audioContext.value.destination);
  } catch (e) {
    console.warn("Web Audio API not supported:", e);
  }
});

onUnmounted(() => {
  window.removeEventListener("resize", updateCardHeights);
  if (currentAudio.value) {
    currentAudio.value.pause();
    currentAudio.value = null;
  }
  if (audioContext.value && audioContext.value.state !== "closed") {
    audioContext.value.close();
  }
});

// Simpler function to update card heights
function updateCardHeights() {
  maxCardHeight.value = 0; // Reset measurement

  // Calculate the height after next render cycle
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
function toggleFavorite(position: number, event?: Event) {
  if (event) {
    event.stopPropagation();
  }
  favoriteTracks.value[position] = !favoriteTracks.value[position];
}

// Play preview if available
async function playPreview(
  previewUrl: string | null,
  position: number,
  event?: Event
) {
  if (event) {
    event.stopPropagation();
  }

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

  if (previewUrl && audioContext.value) {
    try {
      // Resume audio context if suspended (needed for browser autoplay policies)
      if (audioContext.value.state === "suspended") {
        await audioContext.value.resume();
      }

      // Create a new audio element
      const audio = new Audio(previewUrl);
      audio.crossOrigin = "anonymous";

      // Create a media element source and connect to analyzer
      const source = audioContext.value.createMediaElementSource(audio);
      source.connect(analyser.value as AnalyserNode);

      // Set up progress tracking
      audio.ontimeupdate = () => {
        if (audio.duration) {
          audioProgress.value[position] =
            (audio.currentTime / audio.duration) * 100;
        }
      };

      // Start playback
      audio.play();
      currentAudio.value = audio;
      playingTrackId.value = position;
      audioProgress.value[position] = 0;

      // Reset when playback ends
      audio.onended = () => {
        playingTrackId.value = null;
        currentAudio.value = null;
        audioProgress.value[position] = 0;
      };
    } catch (error) {
      console.error("Error playing audio:", error);
    }
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

// Compute if audio is playing and get normalized progress (0-1)
function getAudioInfo(position: number) {
  const isPlaying = playingTrackId.value === position;
  const progress = audioProgress.value[position] ?? 0;

  return {
    isPlaying,
    progress: progress / 100,
  };
}

// Get position badge color based on chart position
function getPositionBadgeColor(position: number) {
  if (position === 1) return "bg-yellow-500 text-black"; // Gold for #1
  if (position === 2) return "bg-gray-300 text-black"; // Silver for #2
  if (position === 3) return "bg-amber-700 text-white"; // Bronze for #3
  if (position <= 10) return "bg-red-600 text-white"; // Red for top 10
  if (position <= 20) return "bg-purple-600 text-white"; // Purple for top 20
  if (position <= 50) return "bg-blue-600 text-white"; // Blue for top 50
  return "bg-black bg-opacity-70 text-white"; // Default black
}
</script>

<template>
  <div class="chart h-full">
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

      <div class="flex flex-wrap gap-4 justify-center">
        <div
          v-for="song in chartStore.chartData.songs"
          :key="song.position"
          class="chart-card-container w-full sm:w-[calc(50%-1rem)] md:w-[calc(33.333%-1rem)] lg:w-[calc(25%-1rem)] xl:w-[calc(25%-1rem)]"
          @mouseenter="toggleFlip(song.position)"
          @mouseleave="toggleFlip(song.position)"
        >
          <div
            class="card-wrapper"
            :style="{ '--min-card-height': `${maxCardHeight}px` }"
          >
            <transition name="p-flip" mode="out-in">
              <!-- Front card -->
              <div
                v-if="!flippedCards[song.position]"
                class="card-face overflow-hidden card-front bg-white rounded-lg shadow-md flex flex-col"
              >
                <div class="relative">
                  <img
                    :src="song.apple_music?.artwork_url || song.image"
                    :alt="`${song.name} by ${song.artist}`"
                    class="w-full aspect-square object-cover"
                    @load="updateCardHeights"
                  />
                  <div
                    class="absolute top-0 left-0 m-2 font-bold rounded-full w-10 h-10 flex items-center justify-center"
                    :class="getPositionBadgeColor(song.position)"
                  >
                    {{ song.position }}
                  </div>

                  <div
                    class="absolute top-0 right-0 m-2"
                    @click="toggleFavorite(song.position, $event)"
                  >
                    <span
                      class="favourite-btn cursor-pointer text-xl"
                      :class="{
                        'pi pi-heart-fill text-red-500':
                          favoriteTracks[song.position],
                        'pi pi-heart text-red-700':
                          !favoriteTracks[song.position],
                      }"
                    ></span>
                  </div>
                </div>

                <div class="p-4 flex flex-col flex-grow">
                  <div class="flex justify-between items-start mb-1">
                    <h3 class="font-bold text-lg" :title="song.name">
                      {{ song.name }}
                    </h3>
                    <div
                      :class="
                        getPositionChangeClass(
                          song.position,
                          song.last_week_position
                        )
                      "
                      class="text-sm font-bold ml-2 whitespace-nowrap"
                    >
                      {{
                        formatPositionChange(
                          song.position,
                          song.last_week_position
                        )
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
                      Peak:
                      <span class="font-medium">{{ song.peak_position }}</span>
                    </div>
                    <div>
                      Weeks:
                      <span class="font-medium">{{ song.weeks_on_chart }}</span>
                    </div>
                    <div v-if="song.last_week_position">
                      Last Week:
                      <span class="font-medium">{{
                        song.last_week_position
                      }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Back card -->
              <div
                v-else
                class="card-face card-back rounded-lg shadow-lg flex flex-col"
                :style="{
                  backgroundImage: `url(${
                    song.apple_music?.artwork_url || song.image
                  })`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }"
              >
                <div
                  class="absolute inset-0 backdrop-blur-sm bg-black/55 rounded-lg"
                ></div>

                <!-- Position Badge -->
                <div
                  class="absolute top-0 left-0 m-2 font-bold rounded-full w-10 h-10 flex items-center justify-center z-10"
                  :class="getPositionBadgeColor(song.position)"
                >
                  {{ song.position }}
                </div>

                <!-- Back Favorite Button -->
                <div
                  class="absolute top-0 right-0 m-2 z-10"
                  @click="toggleFavorite(song.position, $event)"
                >
                  <span
                    class="favourite-btn cursor-pointer text-2xl"
                    :class="{
                      'pi pi-heart-fill text-red-500':
                        favoriteTracks[song.position],
                      'pi pi-heart text-white': !favoriteTracks[song.position],
                    }"
                  ></span>
                </div>

                <!-- Central content -->
                <div
                  class="relative z-10 p-6 flex flex-col items-center justify-center h-full text-white gap-6"
                >
                  <!-- Song Title -->
                  <h3 class="font-bold text-xl text-center">{{ song.name }}</h3>

                  <!-- Artist -->
                  <p class="text-gray-300 text-center">{{ song.artist }}</p>

                  <!-- Play Button -->
                  <div
                    v-if="song.apple_music?.preview_url"
                    class="play-button-container relative cursor-pointer"
                    @click="
                      playPreview(
                        song.apple_music?.preview_url,
                        song.position,
                        $event
                      )
                    "
                  >
                    <!-- Circular progress -->
                    <div
                      class="circular-progress"
                      :style="{
                        background: `conic-gradient(
                          rgba(255, 255, 255, 0.8) ${
                            getAudioInfo(song.position).progress * 360
                          }deg,
                          rgba(255, 255, 255, 0.2) ${
                            getAudioInfo(song.position).progress * 360
                          }deg
                        )`,
                      }"
                    >
                      <div
                        class="inner-circle flex items-center justify-center"
                      >
                        <font-awesome-icon
                          v-if="playingTrackId === song.position"
                          :icon="['fas', 'pause']"
                          size="lg"
                        />
                        <font-awesome-icon
                          v-else
                          :icon="['fas', 'play']"
                          size="lg"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* Add flip animation for PrimeVue transition */
.p-flip-enter-active {
  animation: p-flip-in 0.6s;
}
.p-flip-leave-active {
  animation: p-flip-out 0.6s;
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

.card-wrapper {
  width: 100%;
  min-height: var(--min-card-height, auto);
  display: flex;
}

.card-face {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: var(--min-card-height, auto);
}

.play-button-container {
  width: 80px;
  height: 80px;

  .circular-progress {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(255, 255, 255, 0.2);
    transition: transform 0.3s ease;

    &:hover {
      transform: scale(1.05);
    }

    &:active {
      transform: scale(0.95);
    }
  }

  .inner-circle {
    width: 90%;
    height: 90%;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    color: white;
  }
}

.favourite-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 32px;
  border-radius: 50%;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  &:active {
    transform: scale(0.95);
  }
}
</style>
