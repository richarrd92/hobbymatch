import { Outlet, Navigate, useNavigate } from "react-router-dom";
import "./HomePage.css";

// Main layout wrapping dashboard, navigation, sidebar, and footer
export default function HomePage({ user }) {
  const navigate = useNavigate(); // For navigation
  // Redirect to login if user not logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="home-page">
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
      <main style={{ overflowY: "auto" }}>
        <Outlet /> {/* Nested route content renders here */}
      </main>
      <footer className="footer-bar">
        <p className="footer-text">
          © 2025 HobbyMatch &nbsp;·&nbsp; {/* Copyright notice */}
          <a href="#">About</a> &nbsp;·&nbsp;
          <a href="#">Help</a> &nbsp;·&nbsp;
          <a href="#">Privacy</a>
        </p>
      </footer>
    </div>
  );
}
