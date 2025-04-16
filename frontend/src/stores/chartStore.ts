import { defineStore } from "pinia";
import { fetchChartData } from "@/services/api";
import { formatToday } from "@/utils/dateUtils";
import type { ChartData } from "@/utils/types";

// Simple storage keys
const STORAGE_KEY_CHART_ID = "waveger_chart_id";
const STORAGE_KEY_DATE = "waveger_date";
const STORAGE_KEY_CACHE = "waveger_cache";

// Type for our cache object
type ChartCache = Record<string, ChartData>;

export const useChartStore = defineStore("chart", {
  state: () => {
    return {
      chartData: null as ChartData | null,
      isLoading: false,
      error: null as string | null,

      // Load last selected chart ID or use default
      chartId: sessionStorage.getItem(STORAGE_KEY_CHART_ID) || "hot-100",

      // Load last selected date or use today
      selectedDate: sessionStorage.getItem(STORAGE_KEY_DATE) || formatToday(),
    };
  },

  actions: {
    async fetchChart(id?: string, week?: string, refresh = false) {
      this.isLoading = true;
      this.error = null;

      // Use provided values or defaults from state
      const chartId = id || this.chartId;
      const dateStr = week || this.selectedDate;

      // Update state with these values
      this.chartId = chartId;
      if (week) this.selectedDate = week;

      // Save selections to sessionStorage
      sessionStorage.setItem(STORAGE_KEY_CHART_ID, chartId);
      sessionStorage.setItem(STORAGE_KEY_DATE, this.selectedDate);

      // Create cache key
      const cacheKey = `${chartId}-${dateStr}`;

      try {
        if (!refresh) {
          // Try to get cached data first
          const cachedData = sessionStorage.getItem(STORAGE_KEY_CACHE);
          if (cachedData) {
            const cache = JSON.parse(cachedData) as ChartCache;
            if (cache[cacheKey]) {
              this.chartData = cache[cacheKey];
              this.isLoading = false;
              return;
            }
          }
        }

        // No cache or forced refresh - fetch from API
        const newChartData = await fetchChartData(chartId, dateStr, refresh);
        this.chartData = newChartData;

        // Update cache
        let cache: ChartCache = {};
        const cachedData = sessionStorage.getItem(STORAGE_KEY_CACHE);
        if (cachedData) {
          cache = JSON.parse(cachedData) as ChartCache;
        }

        cache[cacheKey] = newChartData;
        sessionStorage.setItem(STORAGE_KEY_CACHE, JSON.stringify(cache));
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : "Failed to load chart data";
      } finally {
        this.isLoading = false;
      }
    },

    changeChart(id: string) {
      if (id !== this.chartId) {
        this.fetchChart(id);
      }
    },

    setDate(date: string) {
      if (date !== this.selectedDate) {
        this.selectedDate = date;
        this.fetchChart();
      }
    },

    setToday() {
      const today = formatToday();
      this.setDate(today);
    },
  },
});
