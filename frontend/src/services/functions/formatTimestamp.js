// Format time difference into a human-readable string
export default function formatTimestamp(datetimeStr) {
  const date = new Date(datetimeStr);
  const diffMs = Date.now() - date.getTime();

  const diffSecs = Math.floor(diffMs / 1000);
  if (diffSecs < 60) {
    // Return "just now" or seconds ago
    return diffSecs < 5
      ? "just now"
      : `${diffSecs} second${diffSecs !== 1 ? "s" : ""} ago`;
  }

  const diffMins = Math.floor(diffSecs / 60);
  if (diffMins < 60) {
    // Return minutes ago
    return `${diffMins} minute${diffMins !== 1 ? "s" : ""} ago`;
  }

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) {
    // Return hours ago
    return `${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
  }

  const diffDays = Math.floor(diffHours / 24);
  // Return days ago
  return `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`;
}
