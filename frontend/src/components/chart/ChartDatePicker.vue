<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useChartStore } from "@/stores/chartStore";
import { stringToDate, formatDateString } from "@/utils/dateUtils";
import DatePicker from "primevue/datepicker";
import Button from "primevue/button";

const store = useChartStore();

// Create a date object from the store's selected date string
const selectedDate = ref(stringToDate(store.selectedDate));

// Today's date for max date constraint
const today = computed(() => new Date());

// Check if selected date is not today
const isNotToday = computed(() => {
  const todayStr = formatDateString(new Date());
  return store.selectedDate !== todayStr;
});

// When date changes in the picker
function onDateChange(newDate: Date | null) {
  if (newDate) {
    selectedDate.value = newDate;
    store.setDate(formatDateString(newDate));
  }
}

// Go to today function
function goToToday() {
  store.setToday();
  selectedDate.value = new Date();
}

// Keep local state in sync with store
watch(
  () => store.selectedDate,
  (newDateStr) => {
    selectedDate.value = stringToDate(newDateStr);
  }
);
</script>

<template>
  <div class="chart-date-picker flex flex-col gap-1 flex-grow sm:flex-grow-0">
    <label for="chart-select" class="block text-sm font-medium text-gray-700"
      >Select Date</label
    >
    <div class="chart-date-picker__input flex items-center gap-2">
      <DatePicker
        v-model="selectedDate"
        :maxDate="today"
        :disabled="store.isLoading"
        dateFormat="yy-mm-dd"
        showIcon
        inputId="date-picker"
        class="flex-grow sm:flex-grow-0"
        aria-label="Select date"
        @date-select="onDateChange"
      />
      <Button
        v-if="isNotToday"
        @click="goToToday"
        :disabled="store.isLoading"
        label="Today"
        aria-label="Set date to today"
        class="chart-date-picker__button"
      />
    </div>
  </div>
</template>
