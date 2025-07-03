import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import ProfileAvatar from "../components/profile/UserProfile/ProfileAvatar";
import ProfileDetails from "../components/profile/UserProfile/ProfileDetails";
import PhotosGridPlaceholder from "../components/profile/PhotosGridPlaceholder";
import ProfileButtons from "../components/profile/UserProfile/ProfileButtons";
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

  return (
    <div className="user-profile-container">
      {/* Header with avatar and profile details */}
      <div className="user-profile-header">
        <ProfileAvatar
          profilePicUrl={user.profile_pic_url}
          name={user.name}
          email={user.email}
          bio={user.bio}
        />
        <ProfileDetails user={user} formatDate={formatDate} />
      </div>

      {/* Placeholder for photos (future feature) */}
      <PhotosGridPlaceholder />

      {/* Buttons for editing, canceling (go feed), and logging out */}
      <ProfileButtons
        onEdit={() => navigate("/edit-profile")}
        onCancel={() => navigate("/feed")}
        onLogout={logout}
      />
    </div>
  );
}
