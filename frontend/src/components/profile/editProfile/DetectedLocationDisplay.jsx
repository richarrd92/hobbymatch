import "./DetectedLocationDisplay.css";

// Displays the user's detected location if available
export default function DetectedLocationDisplay({ location }) {
  // Return nothing if location is not available
  if (!location) return null;

  return (
    // Container for displaying detected location
    <div className="location-display" style={{ marginTop: "1rem" }}>
      <p>
        Location detected:{" "}
        <strong>
          {location.city}, {location.region}, {location.country}
        </strong>
      </p>
    </div>
  );
}
