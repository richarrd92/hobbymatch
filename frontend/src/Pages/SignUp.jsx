import { useState } from "react";
import { useAuth } from "../services/auth/AuthProvider";
import AuthCard from "../components/AuthCard";

/**
 * SignUp component provides a UI for users to sign up using Google authentication.
 * It uses the AuthProvider context's login function to trigger the sign-in flow,
 * handles loading and error states, and displays an AuthCard component.
 *
 * @returns {JSX.Element} The sign-up UI with a Google sign-in button and status messages.
 */
export default function SignUp() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  /**
   * Handles the sign-up button click by triggering the login flow,
   * showing loading prompt, and handling any errors.
   */
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
