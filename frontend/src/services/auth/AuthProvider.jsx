import { createContext, useContext, useEffect, useState } from "react";
import { firebaseSignIn } from "./firebaseAuth";
import { backendLogin, backendSignup } from "../API/auth";
import {
  saveAuthUser,
  loadAuthUser,
  clearAuthUser,
} from "../functions/authStorage";

// React context to provide global authentication state and functions
const AuthContext = createContext();

/**
 * Provides authentication context to app components.
 * Handles Firebase sign-in and backend login/signup.
 * Loads from localStorage and syncs across tabs.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // Authenticated user data
  const [token, setToken] = useState(null); // Firebase token

  // Load auth state from localStorage on component mount
  useEffect(() => {
    const stored = loadAuthUser();
    if (stored) {
      setUser(stored.user);
      setToken(stored.token);
    }
  }, []);

  // Sync auth state changes across tabs (storage event listener)
  useEffect(() => {
    function handleStorageChange(event) {
      if (event.key === "authUser") {
        if (!event.newValue) {
          // User logged out in another tab
          setUser(null);
          setToken(null);
        } else {
          // User logged in or updated elsewhere in another tab
          const { user: newUser, token: newToken } = JSON.parse(event.newValue);
          setUser(newUser);
          setToken(newToken);
        }
      }
    }

    // Add storage event listener
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  /**
   * Handles login flow:
   * 1. Sign in via Firebase
   * 2. Try backend login
   * 3. If user doesn't exist (404), auto-signup via backend
   */
  const login = async () => {
    try {
      const firebaseToken = await firebaseSignIn();

      try {
        const backendUser = await backendLogin(firebaseToken);
        saveAuthUser({ user: backendUser, token: firebaseToken });
        setUser(backendUser);
        setToken(firebaseToken);
      } catch (err) {
        // If user not found, auto-signup
        if (err.status === 404) {
          const backendUser = await backendSignup(firebaseToken);
          saveAuthUser({ user: backendUser, token: firebaseToken });
          setUser(backendUser);
          setToken(firebaseToken);
        } else {
          throw new Error("Authentication failed");
        }
      }
    } catch (err) {
      console.error("Google sign-in failed", err);
      throw err;
    }
  };

  /**
   * Logs the user out:
   * - Clears auth state
   * - Clears localStorage
   */
  const logout = () => {
    clearAuthUser();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access authentication context.
 * @returns {{ user: object|null, token: string|null, login: Function, logout: Function }}
 */
export function useAuth() {
  return useContext(AuthContext);
}
