import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getUserHobbies, fetchAllHobbies } from "../services/API/hobby";
import "./UserProfile.css";

// Displays user's profile info, photos placeholder, and action buttons
export default function UserProfile({ user }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Format ISO date string to readable local date/time
  const formatDate = (isoString) => {
    if (!isoString) return "N/A";
    return new Date(isoString).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  // Redirect to login if user not logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Profile details
  const loc = user?.location;
  const [hobbies, setHobbies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch user hobbies and categories
  useEffect(() => {
    if (!user) return;

    // Load hobbies and categories
    async function loadHobbiesAndJoin() {
      setLoading(true);
      try {
        const [userHobbyLinks, allHobbies] = await Promise.all([
          getUserHobbies(),
          fetchAllHobbies(),
        ]);

        const enriched = userHobbyLinks.map((link) => {
          const hobby = allHobbies.find((h) => h.id === link.hobby_id);
          return {
            ...link,
            name: hobby?.name || "Unknown",
            category: hobby?.category || "Uncategorized",
          };
        });

        setHobbies(enriched);
      } catch (err) {
        console.error("Error loading hobbies or categories", err);
      } finally {
        setLoading(false);
      }
    }

    // Load hobbies when user changes
    loadHobbiesAndJoin();
  }, [user]);

  // Format hobbies for display
  const hobbySlots = Array.from({ length: 3 }, (_, i) => hobbies[i] || null);

  return (
    <div className="user-profile-container">
      {/* Top section: Avatar + Details */}
      <div className="profile-card">
        {/* Profile picture or fallback avatar */}
        <img
          src={user.profile_pic_url || "/default-avatar.png"}
          alt="avatar"
          className="profile-avatar"
        />

        {/* User details: name, email, and bio */}
        <div>
          <h2 className="profile-name">{user.name || "Unnamed User"}</h2>
          <p className="profile-email">{user.email || "No email provided"}</p>
        </div>
      </div>
      {/* Profile Details section: User Info */}
      <div className="user-profile-info">
        {/* Age */}
        <p className="user-profile-text">
          <strong>Age:</strong> {user.age ?? "Not provided"}
        </p>
        {/* Bio */}
        <p className="user-profile-text">
          <strong>Bio:</strong> {user.bio || "No bio yet"}
        </p>
        {/* Location */}
        <p className="user-profile-text">
          <strong>Location:</strong>{" "}
          {loc
            ? [loc.city, loc.region, loc.country].filter(Boolean).join(", ")
            : "No location set"}
        </p>

        {/* Other user info... */}
        <p className="user-profile-text">
          <strong>Role:</strong> {user.role || "N/A"}
        </p>
        <p className="user-profile-text">
          <strong>Verified:</strong> {user.is_verified ? "Yes" : "No"}
        </p>
        <p className="user-profile-text">
          <strong>Verification Method:</strong>{" "}
          {user.verification_method || "N/A"}
        </p>
        <p className="user-profile-text">
          <strong>Privacy:</strong> {user.is_private ? "Private" : "Public"}
        </p>
        <p className="user-profile-text">
          <strong>Account Created:</strong> {formatDate(user.created_at)}
        </p>
        <p className="user-profile-text">
          <strong>Last Updated:</strong> {formatDate(user.updated_at)}
        </p>
        <p className="user-profile-text">
          <strong>Timezone:</strong> {loc?.timezone || "Unknown"}
        </p>
        <p className="user-profile-text">
          <strong>Coordinates:</strong>{" "}
          {loc
            ? `${loc.latitude?.toFixed(4)}, ${loc.longitude?.toFixed(4)}`
            : "N/A"}
        </p>

        {/* Hobbies */}
        <div className="user-profile-hobbies">
          <p className="user-profile-text">
            <strong>Hobbies:</strong>
          </p>
          {loading ? (
            <p>Loading hobbies...</p>
          ) : (
            <ul className="user-profile-hobby-list">
              {hobbySlots.map((hobbyItem, i) =>
                hobbyItem ? (
                  <li key={hobbyItem.id} className="user-profile-hobby-filled">
                    <span>{hobbyItem.name}</span>
                    <span className="user-profile-hobby-category">
                      {hobbyItem.category}
                    </span>
                  </li>
                ) : (
                  <li
                    key={`placeholder-${i}`}
                    className="user-profile-hobby-placeholder"
                  >
                    Not selected
                  </li>
                )
              )}
            </ul>
          )}
        </div>
      </div>{" "}
      {/* Bottom section: action buttons */}
      <div className="profile-buttons">
        {/* Edit profile button */}
        <button
          className="btn primary-btn"
          onClick={() => navigate("/edit-profile")}
        >
          Edit Profile
        </button>

        {/* Cancel button */}
        <button className="btn secondary-btn" onClick={() => navigate("/feed")}>
          Cancel
        </button>

        {/* Logout button */}
        <button className="btn logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
}
