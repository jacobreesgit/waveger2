<script setup lang="ts">
import { useRouter } from "vue-router";
import Button from "primevue/button";

const router = useRouter();

function navigateToCharts() {
  router.push({ name: "charts" });
}
</script>

<template>
  <div class="home-view p-6 max-w-4xl mx-auto text-center">
    <h1 class="text-4xl font-bold mb-4">Welcome to Waveger</h1>

    <div class="mt-8 flex flex-col items-center gap-8">
      <section class="hero-section">
        <h2 class="text-2xl font-semibold mb-3">Explore Music Charts</h2>
        <p class="text-gray-600 mb-6 max-w-2xl">
          Stay up-to-date with the latest music trends across various Billboard
          charts. View current rankings, track position changes, and listen to
          song previews.
        </p>

        <Button
          label="Browse Charts"
          icon="pi pi-chart-bar"
          class="p-button-lg"
          @click="navigateToCharts"
        />
      </section>

      <section
        class="features grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 w-full"
      >
        <div class="feature-card p-4 bg-gray-50 rounded-lg shadow">
          <i class="pi pi-chart-line text-indigo-600 text-3xl mb-4"></i>
          <h3 class="text-xl font-semibold mb-2">Track Changes</h3>
          <p class="text-gray-600">
            See how songs move up and down the charts each week
          </p>
        </div>

        <div class="feature-card p-4 bg-gray-50 rounded-lg shadow">
          <i class="pi pi-volume-up text-indigo-600 text-3xl mb-4"></i>
          <h3 class="text-xl font-semibold mb-2">Preview Tracks</h3>
          <p class="text-gray-600">
            Listen to song previews directly from the chart view
          </p>
        </div>

        <div class="feature-card p-4 bg-gray-50 rounded-lg shadow">
          <i class="pi pi-calendar text-indigo-600 text-3xl mb-4"></i>
          <h3 class="text-xl font-semibold mb-2">Historical Data</h3>
          <p class="text-gray-600">Access chart data from previous weeks</p>
        </div>
      </section>
    </div>
  </div>
</template>
