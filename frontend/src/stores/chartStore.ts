import { defineStore } from "pinia";
import { fetchChartData } from "@/services/api";
import { formatToday } from "@/utils/dateUtils";
import type { ChartData } from "@/utils/types";

export const useChartStore = defineStore("chart", {
  state: () => {
    const state = {
      chartData: null as ChartData | null,
      isLoading: false,
      error: null as string | null,
      chartId: "hot-100",
      selectedDate: formatToday(),
    };

    return state;
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

      if (import.meta.env.DEV) {
        console.log("[ChartStore] Fetching chart with:", {
          chartId,
          dateStr,
          refresh,
        });
      }

      try {
        // Keep the old data until we have new data
        const newChartData = await fetchChartData(chartId, dateStr, refresh);
        this.chartData = newChartData;

        if (import.meta.env.DEV) {
          console.log(
            "[ChartStore] Chart data loaded successfully:",
            this.chartData
          );
        }
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : "Failed to load chart data";

        if (import.meta.env.DEV) {
          console.error("[ChartStore] Error loading chart data:", this.error);
        }
      } finally {
        this.isLoading = false;
      }
    },

    changeChart(id: string) {
      if (import.meta.env.DEV) {
        console.log("[ChartStore] Changing chart to:", id);
      }
      this.fetchChart(id);
    },

    setDate(date: string) {
      if (import.meta.env.DEV) {
        console.log("[ChartStore] Setting date to:", date);
      }
      this.selectedDate = date;
      this.fetchChart();
    },

    setToday() {
      const today = formatToday();
      if (import.meta.env.DEV) {
        console.log("[ChartStore] Setting date to today:", today);
      }
      this.selectedDate = today;
      this.fetchChart();
    },
  },
});
