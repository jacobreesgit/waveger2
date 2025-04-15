import { defineStore } from "pinia";
import axios from "axios";

// Types
interface ChartEntry {
  position: number;
  title: string;
  artist: string;
  image: string;
  apple_music?: {
    preview_url: string | null;
    artwork_url: string;
    url: string;
  } | null;
}

interface ChartData {
  chart: {
    name: string;
    date: string;
  };
  entries: ChartEntry[];
  cached?: boolean;
}

export const useChartStore = defineStore("chart", {
  state: () => ({
    chartData: null as ChartData | null,
    isLoading: false,
    error: null as string | null,
    chartId: "hot-100",
  }),

  actions: {
    async fetchChart(id = "hot-100") {
      this.isLoading = true;
      this.error = null;
      this.chartId = id;

      try {
        // Use Vite's proxy for development, direct URL in production
        const baseUrl = import.meta.env.DEV
          ? "/api"
          : "https://waveger-api.onrender.com";

        const response = await axios.get(`${baseUrl}/billboard_api.php`, {
          params: { id: this.chartId },
        });

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
