import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import AuthCard from "../components/auth/AuthCard";

// Handles user sign-up via Google using auth context
export default function SignUp() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false); // Loading state during signup
  const [errorMsg, setErrorMsg] = useState(""); // Error message for signup failure

  // Trigger sign-up process (uses login flow)
  const handleSignup = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      await login();
    } catch (err) {
      console.error(err);
      setErrorMsg("Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="HobbyMatch"
      loading={loading}
      loadingText="Creating your account..."
      buttonText="Sign up with Google"
      errorMsg={errorMsg}
      onAuthClick={handleSignup}
      switchText="Already have an account?"
      switchLinkText="Login"
      switchRoute="/login"
    />
  );
}
