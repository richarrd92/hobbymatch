import { useNavigate } from "react-router-dom";
import "./AuthCard.css";

/**
 * AuthCard component displays a reusable card for authentication (login/signup).
 *
 * @param {Object} props
 * @param {string} props.title - The title to display on the card
 * @param {boolean} props.loading - Whether the auth process is in progress
 * @param {string} props.loadingText - Text to show while loading
 * @param {string} props.buttonText - Text on the auth button
 * @param {string} props.errorMsg - Error message to display
 * @param {Function} props.onAuthClick - Function to call on auth button click
 * @param {string} props.switchText - Text to show before the switch link
 * @param {string} props.switchLinkText - Text on the switch link button
 * @param {string} props.switchRoute - Route to navigate when switch link is clicked
 */
export default function AuthCard({
  title,
  loading,
  loadingText,
  buttonText,
  errorMsg,
  onAuthClick,
  switchText,
  switchLinkText,
  switchRoute,
}) {
  const navigate = useNavigate(); // Hook to navigate between routes

  return (
    <div className="auth-card">
      {/* Title text */}
      <h2 className="auth-title">{title}</h2>
      {loading ? (
        // Show loading text if loading
        <p className="auth-loading">{loadingText}</p>
      ) : (
        <>
          {/* Main auth button */}
          <button className="auth-button" onClick={onAuthClick}>
            {buttonText}
          </button>

          {/* Switch to another auth route (e.g., from login to signup) */}
          <p className="auth-switch">
            {switchText}{" "}
            <button className="auth-link" onClick={() => navigate(switchRoute)}>
              {switchLinkText}
            </button>
          </p>

          {/* Show error message if exists */}
          {errorMsg && <p className="auth-error">{errorMsg}</p>}
        </>
      )}
    </div>
  );
}
