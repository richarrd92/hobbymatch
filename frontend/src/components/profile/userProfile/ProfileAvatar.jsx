import "./ProfileAvatar.css";

// Displays a user's avatar, name, email, and bio in a styled card
export default function ProfileAvatar({ profilePicUrl, name, email, bio }) {
  return (
    <div className="profile-card">
      {/* Profile picture or fallback avatar */}
      <img
        src={profilePicUrl || "/default-avatar.png"}
        alt="avatar"
        className="profile-avatar"
      />

      {/* User details: name, email, and bio */}
      <div>
        <h2 className="profile-name">{name || "Unnamed User"}</h2>
        <p className="profile-email">{email || "No email provided"}</p>
        <p className="profile-text">
          <strong>Bio:</strong> {bio || "No bio yet"}
        </p>
      </div>
    </div>
  );
}
