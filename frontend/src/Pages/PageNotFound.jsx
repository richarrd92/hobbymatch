import { useNavigate } from "react-router-dom";
import { useAuth } from "../services/auth/AuthProvider";
import "./PageNotFound.css";

/**
 * PageNotFound component renders a 404 error page with a message,
 * and provides a button that logs the user out and redirects them to the signup page.
 *
 * @returns {JSX.Element} A simple 404 page with logout and redirect functionality.
 */
export default function PageNotFound() {
  const { logout } = useAuth(); 
  const navigate = useNavigate(); 

  /**
   * Handles the logout action and redirects user to the signup page.
   */
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
