import type { ChartOption } from "./types";

/**
 * Available chart options for selection
 */
export const CHART_OPTIONS: ChartOption[] = [
  { id: "hot-100", title: "Billboard Hot 100™" },
  { id: "billboard-200", title: "Billboard 200™" },
  { id: "artist-100", title: "Billboard Artist 100" },
  { id: "emerging-artists", title: "Emerging Artists" },
  { id: "streaming-songs", title: "Streaming Songs" },
  { id: "radio-songs", title: "Radio Songs" },
  { id: "digital-song-sales", title: "Digital Song Sales" },
  { id: "summer-songs", title: "Songs of the Summer" },
  { id: "top-album-sales", title: "Top Album Sales" },
  { id: "top-streaming-albums", title: "Top Streaming Albums" },
  { id: "independent-albums", title: "Independent Albums" },
  { id: "vinyl-albums", title: "Vinyl Albums" },
  { id: "indie-store-album-sales", title: "Indie Store Album Sales" },
  {
    id: "billboard-u-s-afrobeats-songs",
    title: "Billboard U.S. Afrobeats Songs",
  },
];

/**
 * Get position badge color based on chart position
 */
export function getPositionBadgeColor(position: number): string {
  if (position === 1) return "bg-yellow-500 text-black"; // Gold for #1
  if (position === 2) return "bg-gray-300 text-black"; // Silver for #2
  if (position === 3) return "bg-amber-700 text-white"; // Bronze for #3
  if (position <= 10) return "bg-red-600 text-white"; // Red for top 10
  if (position <= 20) return "bg-purple-600 text-white"; // Purple for top 20
  if (position <= 50) return "bg-blue-600 text-white"; // Blue for top 50
  return "bg-black bg-opacity-70 text-white"; // Default black
}

/**
 * Format position change for display
 */
export function formatPositionChange(
  current: number,
  last: number | undefined
): string {
  if (last === undefined || last === 0) return "NEW";
  const diff = last - current;
  if (diff === 0) return "=";
  return diff > 0 ? `↑${diff}` : `↓${Math.abs(diff)}`;
}

/**
 * Get CSS class for position change
 */
export function getPositionChangeClass(
  current: number,
  last: number | undefined
): string {
  if (last === undefined || last === 0) return "text-blue-500";
  const diff = last - current;
  if (diff === 0) return "text-gray-500";
  return diff > 0 ? "text-green-500" : "text-red-500";
}
