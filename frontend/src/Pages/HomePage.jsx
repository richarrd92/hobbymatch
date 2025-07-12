import { Outlet, Navigate, useNavigate } from "react-router-dom";
import "./HomePage.css";

/**
 * HomePage component serves as the main layout wrapper for authenticated users.
 * It includes a top header with logo and avatar, a left sidebar for navigation,
 * a main content area where nested routes render, and a footer.
 * 
 * Redirects to the login page if no user is provided (unauthenticated).
 *
 * @param {Object} props
 * @param {Object|null} props.user - The currently logged-in user object or null if unauthenticated.
 *
 * @returns {JSX.Element} The layout with navigation and nested routes.
 */
export default function HomePage({ user }) {
  const navigate = useNavigate();
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
          Feed
        </button>
        {/* Navigate to Profile */}
        <button className="sidebar-btn" onClick={() => navigate("/profile")}>
          Profile
        </button>
        {/* Navigate to Create post */}
        <button className="sidebar-btn" onClick={() => navigate("/create-post")}>
          Create Post
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
