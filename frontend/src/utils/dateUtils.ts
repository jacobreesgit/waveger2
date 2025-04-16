import dayjs from "dayjs";

/**
 * Convert string date to Date object
 * @param dateStr - Date string in YYYY-MM-DD format
 * @returns Date object
 */
export function stringToDate(dateStr: string): Date {
  if (!dateStr) return new Date();
  return dayjs(dateStr).toDate();
}

/**
 * Format Date to YYYY-MM-DD string
 * @param date - Date object
 * @returns Date string in YYYY-MM-DD format
 */
export function formatDateString(date: Date): string {
  return dayjs(date).format("YYYY-MM-DD");
}

/**
 * Get today's date formatted as YYYY-MM-DD
 * @returns Today's date as string
 */
export function formatToday(): string {
  return dayjs().format("YYYY-MM-DD");
}
