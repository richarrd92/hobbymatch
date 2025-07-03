import "./PhotosGridPlaceholder.css";

// Displays a placeholder for future photo uploads
export default function PhotosGridPlaceholder() {
  return (
    // Container for the photos section
    <div className="profile-photos-section" style={{ marginTop: "1.5rem" }}>
      {/* Placeholder message */}
      <p style={{ fontSize: "0.85rem", color: "#777" }}>
        Upload coming in future updates!
      </p>

      {/* Grid of photo placeholders */}
      <div className="photos-grid">
        <div className="photo-placeholder">📷</div>
        <div className="photo-placeholder">📷</div>
        <div className="photo-placeholder">📷</div>
      </div>
    </div>
  );
}
