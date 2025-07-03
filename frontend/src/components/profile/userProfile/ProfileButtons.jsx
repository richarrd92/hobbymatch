import "./ProfileButtons.css";

// Renders buttons for editing profile, canceling, and logging out
export default function ProfileButtons({ onEdit, onCancel, onLogout }) {
  return (
    <div className="profile-buttons">
      {/* Edit profile button */}
      <button className="btn primary-btn" onClick={onEdit}>
        Edit Profile
      </button>

      {/* Cancel button */}
      <button className="btn secondary-btn" onClick={onCancel}>
        Cancel
      </button>

      {/* Logout button */}
      <button className="btn logout-btn" onClick={onLogout}>
        Logout
      </button>
    </div>
  );
}
