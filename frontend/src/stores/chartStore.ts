import { defineStore } from "pinia";
import { fetchChartData } from "@/services/api";
import { formatToday } from "@/utils/dateUtils";
import type { ChartData } from "@/utils/types";

export const useChartStore = defineStore("chart", {
  state: () => ({
    chartData: null as ChartData | null,
    isLoading: false,
    error: null as string | null,
    chartId: "hot-100",
    selectedDate: formatToday(),
  }),

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

      try {
        this.chartData = await fetchChartData(chartId, dateStr, refresh);
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : "Failed to load chart data";
      } finally {
        this.isLoading = false;
      }
    },

    changeChart(id: string) {
      this.fetchChart(id);
    },

    setDate(date: string) {
      this.selectedDate = date;
      this.fetchChart();
    },

    setToday() {
      this.selectedDate = formatToday();
      this.fetchChart();
    },
  },
});
