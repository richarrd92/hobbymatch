import { useNavigate } from "react-router-dom";
import "./NavBar.css";

// Top navigation bar with logo and user avatar
export default function NavBar({ user }) {
  const navigate = useNavigate();

  return (
    <header className="top-bar">
      {/* App logo */}
      <h1 className="logo">HobbyMatch</h1>

      {/* User avatar; click navigates to profile */}
      <img
        src={user?.profile_pic_url || "/default-avatar.png"}
        alt="avatar"
        className="avatar"
        title="profile"
        onClick={() => navigate("/profile")}
      />
    </header>
  );
}
