<script setup lang="ts">
import { ref } from "vue";
import Button from "primevue/button";
import type { Song } from "@/utils/types";
import {
  getPositionBadgeColor,
  formatPositionChange,
  getPositionChangeClass,
} from "@/utils/chartConstants";

const props = defineProps<{
  song: Song;
  flipped: boolean;
  playingTrackId: number | null;
  audioInfo: { progress: number };
}>();

const emit = defineEmits<{
  (e: "flip", position: number): void;
  (e: "favorite", position: number): void;
  (e: "play", previewUrl: string | null | undefined, position: number): void;
  (e: "volumeChange", volume: number): void;
}>();

// Track favorited state
const isFavorite = ref(false);
const volume = ref(0.8);

// Toggle favorite status
function toggleFavorite(event?: Event) {
  if (event) {
    event.stopPropagation();
  }
  isFavorite.value = !isFavorite.value;
  emit("favorite", props.song.position);
}

// Watch for volume changes
function onVolumeChange(event: Event) {
  if (event.target) {
    const input = event.target as HTMLInputElement;
    volume.value = parseFloat(input.value);
    emit("volumeChange", volume.value);
  }
}

// Handle audio playback
function playPreview(previewUrl: string | null | undefined, event?: Event) {
  if (event) {
    event.stopPropagation();
  }
  emit("play", previewUrl, props.song.position);
}

// External link handlers
function openAppleMusic(url: string | undefined, event?: Event) {
  if (event) {
    event.stopPropagation();
  }
  if (url) {
    window.open(url, "_blank", "noopener,noreferrer");
  }
}

function openChartLink(url: string, event?: Event) {
  if (event) {
    event.stopPropagation();
  }
  window.open(url, "_blank", "noopener,noreferrer");
}
</script>

<template>
  <div class="card-wrapper" @click="emit('flip', song.position)">
    <transition name="p-flip" mode="out-in">
      <!-- Front card -->
      <div
        v-if="!flipped"
        class="card-face overflow-hidden card-front bg-white rounded-lg shadow-md flex flex-col h-full"
      >
        <div class="relative">
          <img
            :src="song.apple_music?.artwork_url || song.image"
            :alt="`${song.name} by ${song.artist}`"
            class="w-full aspect-square object-cover"
            loading="lazy"
          />
          <div
            class="absolute top-0 left-0 m-2 font-bold rounded-full w-10 h-10 flex items-center justify-center"
            :class="getPositionBadgeColor(song.position)"
          >
            {{ song.position }}
          </div>

          <Button
            @click="toggleFavorite($event)"
            class="p-button-rounded absolute! top-0! right-0! m-2 bg-white/80! hover:bg-white! cursor-pointer border-0! w-8! h-8!"
          >
            <span
              class="text-xl"
              :class="{
                'pi pi-heart-fill text-red-500': isFavorite,
                'pi pi-heart text-red-700': !isFavorite,
              }"
            ></span>
          </Button>
        </div>

        <div class="p-4 flex flex-col flex-grow">
          <div class="flex justify-between items-start mb-1">
            <h3 class="font-bold text-lg line-clamp-2" :title="song.name">
              {{ song.name }}
            </h3>
            <div
              :class="
                getPositionChangeClass(song.position, song.last_week_position)
              "
              class="text-sm font-bold ml-2 whitespace-nowrap"
            >
              {{ formatPositionChange(song.position, song.last_week_position) }}
            </div>
          </div>

          <p class="text-gray-600 mb-2 line-clamp-1" :title="song.artist">
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
              Last:
              <span class="font-medium">{{ song.last_week_position }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Back card -->
      <div
        v-else
        class="card-face card-back rounded-lg shadow-lg flex flex-col h-full"
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

        <!-- Back Card Controls -->
        <Button
          @click="toggleFavorite($event)"
          class="p-button-rounded absolute! top-0! right-0! m-2 bg-white/30! hover:bg-white/60! cursor-pointer border-0! w-8! h-8!"
        >
          <span
            class="text-xl"
            :class="{
              'pi pi-heart-fill text-red-500': isFavorite,
              'pi pi-heart text-white': !isFavorite,
            }"
          ></span>
        </Button>

        <!-- Central content -->
        <div
          class="relative z-10 p-6 flex flex-col items-center justify-center h-full text-white gap-4"
        >
          <!-- Song Title -->
          <h3 class="font-bold text-xl text-center">{{ song.name }}</h3>

          <!-- Artist -->
          <p class="text-gray-300 text-center">{{ song.artist }}</p>

          <!-- Stats Display -->
          <div class="stats-display grid grid-cols-3 gap-3 w-full mb-2">
            <div class="stat-item flex flex-col items-center">
              <span class="text-gray-300 text-xs">Position</span>
              <span class="font-bold text-lg text-white">{{
                song.position
              }}</span>
            </div>
            <div class="stat-item flex flex-col items-center">
              <span class="text-gray-300 text-xs">Peak</span>
              <span class="font-bold text-lg text-white">{{
                song.peak_position
              }}</span>
            </div>
            <div class="stat-item flex flex-col items-center">
              <span class="text-gray-300 text-xs">Weeks</span>
              <span class="font-bold text-lg text-white">{{
                song.weeks_on_chart
              }}</span>
            </div>
          </div>

          <!-- Play Button -->
          <div
            v-if="song.apple_music?.preview_url"
            class="play-container flex flex-col items-center gap-2 w-full"
          >
            <!-- Circular progress -->
            <div
              class="play-button-container relative cursor-pointer"
              @click.stop="playPreview(song.apple_music?.preview_url, $event)"
            >
              <div
                class="circular-progress"
                :style="{
                  background: `conic-gradient(
                    rgba(255, 255, 255, 0.8) ${audioInfo.progress * 360}deg,
                    rgba(255, 255, 255, 0.2) ${audioInfo.progress * 360}deg
                  )`,
                }"
              >
                <div class="inner-circle flex items-center justify-center">
                  <font-awesome-icon
                    v-if="playingTrackId === song.position"
                    :icon="['fas', 'pause']"
                    class="text-2xl"
                  />
                  <font-awesome-icon
                    v-else
                    :icon="['fas', 'play']"
                    class="text-2xl"
                  />
                </div>
              </div>
            </div>

            <!-- Volume Control -->
            <div
              class="volume-control w-full max-w-[160px] flex items-center gap-2"
            >
              <span class="pi pi-volume-down text-sm"></span>
              <input
                type="range"
                v-model="volume"
                min="0"
                max="1"
                step="0.1"
                class="flex-grow"
                @click.stop
                @input="onVolumeChange"
              />
              <span class="pi pi-volume-up text-sm"></span>
            </div>
          </div>

          <!-- External Links section -->
          <div class="external-links flex gap-2 mt-2">
            <Button
              v-if="song.apple_music?.url"
              @click="(e) => openAppleMusic(song.apple_music?.url, e)"
              class="p-button-rounded bg-white/30! hover:bg-white/60! cursor-pointer border-0! w-8! h-8!"
            >
              <font-awesome-icon :icon="['fab', 'apple']" class="text-white" />
            </Button>
            <Button
              @click="(e) => openChartLink(song.url, e)"
              class="p-button-rounded bg-white/30! hover:bg-white/60! cursor-pointer border-0! w-8! h-8!"
            >
              <font-awesome-icon
                :icon="['fas', 'chart-line']"
                class="text-white"
              />
            </Button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.card-wrapper {
  width: 100%;
  min-height: var(--min-card-height, auto);
  display: flex;
  transition: transform 0.2s ease-in-out;
  perspective: 1500px;
  transform-style: preserve-3d;
  will-change: transform;

  &:hover {
    transform: translateY(-4px);
  }
}

.card-face {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: var(--min-card-height, auto);
  transition: box-shadow 0.2s ease;
  backface-visibility: hidden;
  transform-style: preserve-3d;
  will-change: transform, opacity;
  -webkit-transform: translateZ(0);
  transform: translateZ(0);

  &:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
      0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
}

.play-button-container {
  width: 64px;
  height: 64px;

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
    width: 85%;
    height: 85%;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

input[type="range"] {
  appearance: none;
  -webkit-appearance: none;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;

  &::-webkit-slider-thumb {
    appearance: none;
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }
}
</style>
