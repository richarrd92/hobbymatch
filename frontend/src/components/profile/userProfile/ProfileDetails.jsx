import "./ProfileDetails.css";

// Displays detailed user profile information
export default function ProfileDetails({ user, formatDate }) {
  const loc = user.location;

  return (
    <div className="profile-info">
      {/* Age */}
      <p className="profile-text">
        <strong>Age:</strong> {user.age ?? "Not provided"}
      </p>

      {/* Location (formatted from available fields) */}
      <p className="profile-text">
        <strong>Location:</strong>{" "}
        {loc
          ? [loc.city, loc.region, loc.country].filter(Boolean).join(", ")
          : "No location set"}
      </p>

      {/* Role */}
      <p className="profile-text">
        <strong>Role:</strong> {user.role || "N/A"}
      </p>

      {/* Verification status */}
      <p className="profile-text">
        <strong>Verified:</strong> {user.is_verified ? "Yes" : "No"}
      </p>

      {/* Verification method */}
      <p className="profile-text">
        <strong>Verification Method:</strong>{" "}
        {user.verification_method || "N/A"}
      </p>

      {/* Privacy setting */}
      <p className="profile-text">
        <strong>Privacy:</strong> {user.is_private ? "Private" : "Public"}
      </p>

      {/* Account creation date */}
      <p className="profile-text">
        <strong>Account Created:</strong> {formatDate(user.created_at)}
      </p>

      {/* Last update date */}
      <p className="profile-text">
        <strong>Last Updated:</strong> {formatDate(user.updated_at)}
      </p>

      {/* Timezone */}
      <p className="profile-text">
        <strong>Timezone:</strong> {loc?.timezone || "Unknown"}
      </p>

      {/* Coordinates */}
      <p className="profile-text">
        <strong>Coordinates:</strong>{" "}
        {loc
          ? `${loc.latitude?.toFixed(4)}, ${loc.longitude?.toFixed(4)}`
          : "N/A"}
      </p>
    </div>
  );
}
