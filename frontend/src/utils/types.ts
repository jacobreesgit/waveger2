/**
 * Song data structure
 */
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

/**
 * Chart data structure
 */
export interface ChartData {
  cached: boolean;
  info: string;
  note?: string;
  songs: Song[];
  title: string;
  week: string;
}

/**
 * Chart option for dropdown
 */
export interface ChartOption {
  id: string;
  title: string;
}
