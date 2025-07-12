import { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useAuth } from "./services/auth/AuthProvider";
import SignUp from "./Pages/SignUp";
import Login from "./Pages/Login";
import PageNotFound from "./Pages/PageNotFound";
import Feed from "./Pages/Feed";
import EditProfile from "./Pages/EditProfile";
import UserProfile from "./Pages/UserProfile";
import PrivateRoute from "../src/Pages/PrivateRoute";
import HomePage from "./Pages/HomePage";
import CreatePost from "./Pages/CreatePost";


/**
 * Main application component managing routing, authentication state, 
 * and user data fetching.
 *
 * Fetches current user info from backend when authentication token changes.
 * Uses protected routes to guard user-only pages.
 *
 * @component
 * @returns {JSX.Element} The app router with routes for login, signup, feed, profile, etc.
 */
export default function App() {
  const { token } = useAuth();

  // State for current user info, loading, errors, and refresh flag
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [userError, setUserError] = useState(null);
  const [refreshFlag, setRefreshFlag] = useState(false);

  useEffect(() => {
    /**
     * Fetches the current user's profile data from the backend API.
     * Triggers when token or refreshFlag changes.
     * Updates the user state and loading/error flags accordingly.
     *
     * @async
     * @throws {Error} - If the response is not OK.
     */
    const fetchUser = async () => {
      setLoadingUser(true);
      try {
        const response = await fetch("http://localhost:8000/users/me", {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        // Throw error if response not ok
        if (!response.ok) throw new Error(await response.text());

        // Set user info
        const data = await response.json();
        setUser(data);
      } catch (err) {
        setUserError(err.message);
        setUser(null);
      } finally {
        setLoadingUser(false);
      }
    };

    if (token) {
      fetchUser();
    } else {
      // No token means no user
      setUser(null);
      setLoadingUser(false);
    }
  }, [token, refreshFlag]);

  // Show loading or error while fetching user data
  if (loadingUser) return <div>Loading user info...</div>;
  if (userError) return <div>Error loading user: {userError}</div>;

  /**
   * Protected dashboard component wrapping the home page.
   * @returns {JSX.Element} HomePage component with user info.
   */
  function ProtectedDashboard() {
    return <HomePage user={user} />;
  }

  return (
    <Router>
      <Routes>
        {/* Public routes: signup and login */}
        <Route
          path="/sign-up"
          element={!user ? <SignUp /> : <Navigate to="/feed" replace />}
        />
        <Route
          path="/login"
          element={!user ? <Login /> : <Navigate to="/feed" replace />}
        />

        {/* Protected routes wrapped in PrivateRoute */}
        <Route element={<PrivateRoute />}>
          <Route path="/" element={<ProtectedDashboard />}>
            <Route index element={<Navigate to="feed" replace />} />
            <Route path="feed" element={<Feed user={user} token={token} />} />
            <Route
              path="profile"
              element={
                <UserProfile
                  user={user}
                  triggerRefresh={() => setRefreshFlag((prev) => !prev)}
                />
              }
            />
            <Route
              path="edit-profile"
              element={
                <EditProfile
                  user={user}
                  triggerRefresh={() => setRefreshFlag((prev) => !prev)}
                />
              }
            />
            <Route path="create-post" element={<CreatePost user={user} />} />
            <Route path="*" element={<PageNotFound />} />
          </Route>
        </Route>
        {/* Catch-all for unknown paths redirects to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}
