import { useNavigate } from "react-router-dom";
import "./AuthCard.css";

// Main Login/SignUp card component
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
