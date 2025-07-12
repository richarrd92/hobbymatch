 /**
 * Formats an ISO date string into a localized, human-readable date and time string.
 *
 * @param {string} isoString - The ISO 8601 formatted date string to format.
 * @returns {string} - A localized date and time string (e.g., "Apr 27, 2025, 3:30 PM") or "N/A" if input is invalid.
 */
  export default function formatDate(isoString){
    if (!isoString) return "N/A";
    return new Date(isoString).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };