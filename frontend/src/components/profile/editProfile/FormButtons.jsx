import "./FormButtons.css";

// Renders form action buttons: location request, save, and cancel
export default function FormButtons({ loading, onRequestLocation, onCancel }) {
  return (
    // Button container with spacing and wrapping
    <div
      style={{
        display: "flex",
        gap: "1rem",
        marginTop: "0.5rem",
        flexWrap: "wrap",
        width: "100%",
      }}
      className="location-section"
    >
      {/* Button to request current location */}
      <button
        type="button"
        className="location-button btn btn-secondary"
        onClick={onRequestLocation}
        disabled={loading}
      >
        📍 Use My Current Location
      </button>

      {/* Submit button with loading state */}
      <button type="submit" className="btn primary-btn" disabled={loading}>
        {loading ? "Saving..." : "Save and Continue"}
      </button>

      {/* Cancel button */}
      <button
        type="button"
        className="btn btn-secondary"
        onClick={onCancel}
        disabled={loading}
      >
        Cancel
      </button>
    </div>
  );
}
