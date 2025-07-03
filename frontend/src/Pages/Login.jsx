import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import AuthCard from "../components/auth/AuthCard";

// Handles user login via Google using auth context
export default function Login() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false); // Loading state during login
  const [errorMsg, setErrorMsg] = useState(""); // Error message to show if login fails

  // Trigger login process
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
