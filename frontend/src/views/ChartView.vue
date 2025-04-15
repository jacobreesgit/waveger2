<script setup lang="ts">
import Chart from "@/components/Chart.vue";
import ChartSelector from "@/components/ChartSelector.vue";
import ChartDatePicker from "@/components/ChartDatePicker.vue";
</script>

<template>
  <div class="chart-view flex flex-col gap-6 max-w-[1200px]">
    <div
      class="chart-view__chart-controls flex w-full gap-2 sm:gap-4 flex-wrap sm:flex-nowrap"
    >
      <ChartSelector />
      <ChartDatePicker />
    </div>

    <Chart></Chart>
  </div>
</template>

<style lang="scss" scoped></style>
