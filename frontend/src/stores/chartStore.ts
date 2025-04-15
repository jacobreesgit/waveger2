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
  }),

  actions: {
    async fetchChart(id = "hot-100", week?: string, refresh = false) {
      this.isLoading = true;
      this.error = null;
      this.chartId = id;

      try {
        // Use Vite's proxy for development, direct URL in production
        const baseUrl = import.meta.env.DEV
          ? "/api"
          : "https://waveger-api.onrender.com";

        // Prepare query parameters
        const params: Record<string, string | boolean> = {
          id: this.chartId,
        };

        // Add week parameter if provided
        if (week) {
          params.week = week;
        }

        // Add refresh parameter if true
        if (refresh) {
          params.refresh = true;
        }

        const response = await axios.get(`${baseUrl}/billboard_api.php`, {
          params,
        });
        console.log("Fetched chart data:", response);
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
  },
});
