import { useNavigate } from "react-router-dom";
import "./AuthCard.css";

export default function AuthCard({
  title, // Form title (e.g., "Sign In", "Register")
  loading, // Boolean to show loading state
  loadingText, // Text shown while loading
  buttonText, // Main action button text
  errorMsg, // Error message to display
  onAuthClick, // Handler for main button click
  switchText, // Text before switch link
  switchLinkText, // Switch route button text (e.g., "Sign up")
  switchRoute, // Route to navigate to on switch
}) {
  const navigate = useNavigate(); // Hook to navigate between routes

  return (
    <div className="auth-card">
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
