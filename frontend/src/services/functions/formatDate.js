  // Format ISO date string to readable local date/time
  export default function formatDate(isoString){
    if (!isoString) return "N/A";
    return new Date(isoString).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };