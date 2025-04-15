import { defineStore } from "pinia";
import axios from "axios";

// Types that match the actual API structure
export interface Song {
  position: number;
  name: string;
  artist: string;
  image: string;
  last_week_position: number;
  peak_position: number;
  weeks_on_chart: number;
  apple_music?: {
    artwork_url: string;
    preview_url: string | null;
    url: string;
    id?: string;
  } | null;
  url: string;
}

export interface ChartData {
  cached: boolean;
  info: string;
  note?: string;
  songs: Song[];
  title: string;
  week: string;
}

export const useChartStore = defineStore("chart", {
  state: () => ({
    chartData: null as ChartData | null,
    isLoading: false,
    error: null as string | null,
    chartId: "hot-100",
    selectedDate: formatToday(), // Store the date in the store
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
        // Use Vite's proxy for development, direct URL in production
        const baseUrl = import.meta.env.DEV
          ? "/api"
          : "https://waveger-api.onrender.com";

        // Prepare query parameters
        const params: Record<string, string | boolean> = {
          id: chartId,
        };

        // Add week parameter if provided
        if (dateStr) params.week = dateStr;
        // Add refresh parameter if true
        if (refresh) params.refresh = true;

        console.log(
          "Making request to:",
          `${baseUrl}/billboard_api.php`,
          "with params:",
          params
        );

        const response = await axios.get(`${baseUrl}/billboard_api.php`, {
          params,
        });

        console.log("Fetched chart data");
        this.chartData = response.data;
      } catch (error) {
        console.error("Error fetching chart data:", error);
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

// Helper function to format today's date
function formatToday(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
