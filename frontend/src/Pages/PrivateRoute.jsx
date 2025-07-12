import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../services/auth/AuthProvider";

/**
 * PrivateRoute component protects nested routes by checking user authentication.
 * It verifies the presence of an auth token from the AuthProvider context.
 * If no token is found (user not authenticated), it redirects to the sign-up page.
 * Otherwise, it renders the child routes/components.
 *
 * @returns {JSX.Element} Redirects to sign-up if unauthenticated, otherwise renders nested routes.
 */
export default function PrivateRoute() {
  const { token } = useAuth();

  // Redirect to sign-up if no token found (not authenticated)
  if (!token) {
    return <Navigate to="/sign-up" replace />;
  }

  // Render child routes if authenticated
  return <Outlet />;
}
