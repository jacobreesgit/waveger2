<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";

export interface LoadingSpinnerProps {
  size?: "small" | "medium" | "large" | "custom";
  customSize?: string;
  strokeWidth?: string;
  fill?: string;
  animationDuration?: string;
  label?: string;
  centerInContainer?: boolean;
}

const props = withDefaults(defineProps<LoadingSpinnerProps>(), {
  size: "medium",
  customSize: "",
  strokeWidth: "4px",
  fill: "#f3f3f3",
  animationDuration: "1s",
  label: "Loading...",
  centerInContainer: true,
});

const spinnerSize = () => {
  if (props.customSize) return props.customSize;
  switch (props.size) {
    case "small":
      return "20px";
    case "large":
      return "60px";
    case "medium":
    default:
      return "60px";
  }
};

const labelFontSize = () => {
  switch (props.size) {
    case "small":
      return "0.75rem";
    case "large":
      return "1.25rem";
    case "medium":
    default:
      return "1rem";
  }
};
</script>

<template>
  <div
    :class="[
      'loading-spinner-wrapper inline-flex flex-col items-center gap-4',
      {
        'loading-spinner-wrapper--center-container flex justify-center items-center w-full min-h-[100px] h-full':
          centerInContainer,
      },
    ]"
  >
    <ProgressSpinner
      :style="{
        width: spinnerSize(),
        height: spinnerSize(),
      }"
      :strokeWidth="strokeWidth"
      :animationDuration="animationDuration"
      aria-label="Loading"
    />
    <p
      v-if="label"
      class="loading-spinner-wrapper__loading-label text-gray-600 text-center"
      :style="{ fontSize: labelFontSize() }"
    >
      {{ label }}
    </p>
  </div>
</template>
