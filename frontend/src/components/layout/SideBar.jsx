import { useNavigate } from "react-router-dom";
import "./SideBar.css";

// Sidebar for navigation
export default function SideBar() {
  const navigate = useNavigate(); // For navigation

  return (
    <aside className="left-sidebar">
      {/* Navigate to Feed */}
      <button className="sidebar-btn" onClick={() => navigate("/feed")}>
        Home
      </button>
      {/* Navigate to Profile */}
      <button className="sidebar-btn" onClick={() => navigate("/profile")}>
        Profile
      </button>
      <button className="sidebar-btn" onClick={() => navigate("/feed")}>
        <span style={{ color: "lightgray" }}>More Coming soon</span>
      </button>
    </aside>
  );
}
