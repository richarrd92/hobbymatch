import { useState } from "react";
import { useAuth } from "../services/auth/AuthProvider";
import AuthCard from "../components/AuthCard";

/**
 * Login component handles user login via Google using the auth context.
 * It manages loading and error states, triggers the login process,
 * and redirects to the feed page upon successful login.
 *
 * @returns {JSX.Element} A login UI card with Google sign-in button and error handling.
 */
export default function Login() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  /**
   * Handles the login button click: performs login, manages states,
   * and redirects on success. Shows error message on failure.
   */
  const handleLogin = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      await login();
      // Redirect to feed after successful login
      window.location.href = "/feed";
    } catch (err) {
      console.error(err);
      setErrorMsg("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="HobbyMatch"
      loading={loading}
      loadingText="Logging in..."
      buttonText="Log in with Google"
      errorMsg={errorMsg}
      onAuthClick={handleLogin}
      switchText="New user?"
      switchLinkText="Sign up"
      switchRoute="/sign-up"
    />
  );
}
