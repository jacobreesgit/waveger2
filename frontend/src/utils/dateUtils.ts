/**
 * Convert string date to Date object
 * @param dateStr - Date string in YYYY-MM-DD format
 * @returns Date object
 */
export function stringToDate(dateStr: string): Date {
  if (!dateStr) return new Date();
  return new Date(dateStr);
}

/**
 * Format Date to YYYY-MM-DD string
 * @param date - Date object
 * @returns Date string in YYYY-MM-DD format
 */
export function formatDateString(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/**
 * Get today's date formatted as YYYY-MM-DD
 * @returns Today's date as string
 */
export function formatToday(): string {
  return formatDateString(new Date());
}
