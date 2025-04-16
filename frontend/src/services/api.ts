// frontend/src/services/api.ts
import axios from "axios";
import type { ChartData } from "@/utils/types";

// Base URL based on environment
const BASE_URL = import.meta.env.DEV
  ? "/api"
  : "https://waveger-api.onrender.com";

/**
 * Fetch chart data from the API
 * @param chartId - ID of the chart to fetch
 * @param week - Optional date string for specific week
 * @param includeAppleMusic - Whether to include Apple Music data
 * @param refresh - Force refresh from source
 * @returns Promise with chart data
 */
export async function fetchChartData(
  chartId: string,
  week?: string,
  includeAppleMusic = true,
  refresh = false
): Promise<ChartData> {
  // Prepare query parameters
  const params: Record<string, string | boolean> = {
    id: chartId,
    apple_music: includeAppleMusic,
  };

  // Add week parameter if provided
  if (week) params.week = week;

  // Add refresh parameter if true
  if (refresh) params.refresh = true;

  try {
    const response = await axios.get(`${BASE_URL}/billboard_api.php`, {
      params,
    });

    return response.data;
  } catch (error) {
    // Re-throw with more context
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Unknown error fetching chart data";

    throw new Error(`Chart API Error: ${errorMessage}`);
  }
}
