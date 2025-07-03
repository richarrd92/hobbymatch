import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./PageNotFound.css";

// 404 page with logout and redirect button
export default function PageNotFound() {
  const { logout } = useAuth(); // Get logout function
  const navigate = useNavigate(); // For navigation

  // Logout and navigate to signup page
  const handleLogout = () => {
    logout();
    navigate("/signup");
  };

  return (
    <div className="page-not-found">
      <h2>404 — Page Not Found</h2>
      <p>Sorry, the page you're looking for doesn't exist.</p>
      {/* Button triggers logout and navigation */}
      <button className="btn btn-primary" onClick={handleLogout}>
        Logout & Go Home
      </button>
    </div>
  );
}
