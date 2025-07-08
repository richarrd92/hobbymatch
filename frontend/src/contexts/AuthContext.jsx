import { createContext, useContext, useEffect, useState } from "react";
import { firebaseSignIn } from "../services/auth/firebaseAuth";
import { backendLogin, backendSignup } from "../services/API/auth";
import {
  saveAuthUser,
  loadAuthUser,
  clearAuthUser,
} from "../services/functions/authStorage";

const AuthContext = createContext();

// Provides authentication context using Firebase and backend login/signup
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // Authenticated user data
  const [token, setToken] = useState(null); // Firebase token

  // Load stored auth data on mount
  useEffect(() => {
    const stored = loadAuthUser();
    if (stored) {
      setUser(stored.user);
      setToken(stored.token);
    }
  }, []);

  // Login flow: Firebase sign-in, then backend login or signup
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

  // Logout clears storage and resets state
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

// Custom hook to use auth context
export function useAuth() {
  return useContext(AuthContext);
}
