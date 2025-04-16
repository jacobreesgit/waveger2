import { defineStore } from "pinia";
import { fetchChartData } from "@/services/api";
import { formatToday } from "@/utils/dateUtils";
import type { ChartData } from "@/utils/types";

// Simple storage keys
const STORAGE_KEY_CHART_ID = "waveger_chart_id";
const STORAGE_KEY_DATE = "waveger_date";
const STORAGE_KEY_CACHE_BASIC = "waveger_cache_basic";
const STORAGE_KEY_CACHE_ENRICHED = "waveger_cache_enriched";

// Type for our cache object
type ChartCache = Record<string, ChartData>;

export const useChartStore = defineStore("chart", {
  state: () => {
    return {
      // Chart data (basic version without Apple Music)
      basicChartData: null as ChartData | null,

      // Loading states
      isLoadingBasic: false,
      isLoadingEnriched: false,

      // Whether we have enriched data (with Apple Music)
      hasEnrichedData: false,

      error: null as string | null,

      // Load last selected chart ID or use default
      chartId: sessionStorage.getItem(STORAGE_KEY_CHART_ID) || "hot-100",

      // Load last selected date or use today
      selectedDate: sessionStorage.getItem(STORAGE_KEY_DATE) || formatToday(),
    };
  },

  getters: {
    // Combined loading state to show to user
    isLoading: (state) => state.isLoadingBasic || state.isLoadingEnriched,

    // Get chart data (basic is always available)
    chartData: (state) => state.basicChartData,
  },

  actions: {
    /**
     * Get cached chart data if available
     * @param type - "basic" or "enriched"
     * @param chartId - Chart ID
     * @param dateStr - Date string
     * @returns Cached data or null
     */
    getCachedData(
      type: "basic" | "enriched",
      chartId: string,
      dateStr: string
    ): ChartData | null {
      const cacheKey = `${chartId}-${dateStr}`;
      const storageKey =
        type === "basic" ? STORAGE_KEY_CACHE_BASIC : STORAGE_KEY_CACHE_ENRICHED;

      const cachedData = sessionStorage.getItem(storageKey);
      if (cachedData) {
        try {
          const cache = JSON.parse(cachedData) as ChartCache;
          if (cache[cacheKey]) {
            return cache[cacheKey];
          }
        } catch (e) {
          console.error("Error parsing cached data:", e);
        }
      }

      return null;
    },

    /**
     * Save data to cache
     * @param type - "basic" or "enriched"
     * @param chartId - Chart ID
     * @param dateStr - Date string
     * @param data - Chart data to cache
     */
    saveCachedData(
      type: "basic" | "enriched",
      chartId: string,
      dateStr: string,
      data: ChartData
    ) {
      const cacheKey = `${chartId}-${dateStr}`;
      const storageKey =
        type === "basic" ? STORAGE_KEY_CACHE_BASIC : STORAGE_KEY_CACHE_ENRICHED;

      // Get existing cache or create new one
      let cache: ChartCache = {};
      const cachedData = sessionStorage.getItem(storageKey);

      if (cachedData) {
        try {
          cache = JSON.parse(cachedData) as ChartCache;
        } catch (e) {
          console.error("Error parsing cached data:", e);
        }
      }

      // Add new data to cache
      cache[cacheKey] = data;
      sessionStorage.setItem(storageKey, JSON.stringify(cache));
    },

    /**
     * Remove basic cached data when we have enriched data
     * @param chartId - Chart ID
     * @param dateStr - Date string
     */
    clearBasicCache(chartId: string, dateStr: string) {
      const cacheKey = `${chartId}-${dateStr}`;
      const cachedData = sessionStorage.getItem(STORAGE_KEY_CACHE_BASIC);

      if (cachedData) {
        try {
          const cache = JSON.parse(cachedData) as ChartCache;
          if (cache[cacheKey]) {
            delete cache[cacheKey];
            sessionStorage.setItem(
              STORAGE_KEY_CACHE_BASIC,
              JSON.stringify(cache)
            );
          }
        } catch (e) {
          console.error("Error clearing basic cache:", e);
        }
      }
    },

    /**
     * Fetch both basic and enriched chart data
     */
    async fetchChart(id?: string, week?: string, refresh = false) {
      // Update chart id and date if provided
      const chartId = id || this.chartId;
      const dateStr = week || this.selectedDate;

      this.chartId = chartId;
      if (week) this.selectedDate = week;

      // Save selections to sessionStorage
      sessionStorage.setItem(STORAGE_KEY_CHART_ID, chartId);
      sessionStorage.setItem(STORAGE_KEY_DATE, this.selectedDate);

      // Check for cached enriched data first (best case scenario)
      if (!refresh) {
        const enrichedCachedData = this.getCachedData(
          "enriched",
          chartId,
          dateStr
        );
        if (enrichedCachedData) {
          this.basicChartData = enrichedCachedData;
          this.hasEnrichedData = true;
          return; // We already have the best data, no need to fetch anything
        }

        // If no enriched data, check for basic cached data
        const basicCachedData = this.getCachedData("basic", chartId, dateStr);
        if (basicCachedData) {
          this.basicChartData = basicCachedData;

          // We have basic data, but still need to fetch enriched data
          this.fetchEnrichedData(chartId, dateStr, refresh);
          return;
        }
      }

      // No cached data or refresh requested, fetch basic data first
      this.fetchBasicData(chartId, dateStr, refresh);
    },

    /**
     * Fetch basic chart data (fast)
     */
    async fetchBasicData(chartId: string, dateStr: string, refresh: boolean) {
      this.isLoadingBasic = true;
      this.error = null;

      try {
        const basicData = await fetchChartData(
          chartId,
          dateStr,
          false,
          refresh
        );
        this.basicChartData = basicData;

        // Cache basic data
        if (!refresh) {
          this.saveCachedData("basic", chartId, dateStr, basicData);
        }

        // Now fetch enriched data
        this.fetchEnrichedData(chartId, dateStr, refresh);
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : "Failed to load chart data";
      } finally {
        this.isLoadingBasic = false;
      }
    },

    /**
     * Fetch enriched chart data (with Apple Music)
     */
    async fetchEnrichedData(
      chartId: string,
      dateStr: string,
      refresh: boolean
    ) {
      this.isLoadingEnriched = true;
      this.hasEnrichedData = false;

      fetchChartData(chartId, dateStr, true, refresh)
        .then((enrichedData) => {
          // Update songs with enriched data
          if (this.basicChartData && this.basicChartData.songs) {
            this.basicChartData.songs = enrichedData.songs;
            this.hasEnrichedData = true;

            // Cache enriched data
            if (!refresh) {
              this.saveCachedData(
                "enriched",
                chartId,
                dateStr,
                this.basicChartData
              );

              // Clear basic cache since we now have enriched data
              this.clearBasicCache(chartId, dateStr);
            }
          }
        })
        .catch((error) => {
          console.error("Failed to load enriched data:", error);
        })
        .finally(() => {
          this.isLoadingEnriched = false;
        });
    },

    /**
     * Change the selected chart
     */
    changeChart(id: string) {
      if (id !== this.chartId) {
        this.fetchChart(id);
      }
    },

    /**
     * Set the date for chart data
     */
    setDate(date: string) {
      if (date !== this.selectedDate) {
        this.selectedDate = date;
        this.fetchChart();
      }
    },

    /**
     * Set date to today
     */
    setToday() {
      const today = formatToday();
      this.setDate(today);
    },
  },
});
