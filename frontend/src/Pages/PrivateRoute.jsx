import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

// Protects routes by checking authentication token
export default function PrivateRoute() {
  const { token } = useAuth();

  // Redirect to sign-up if no token found (not authenticated)
  if (!token) {
    return <Navigate to="/sign-up" replace />;
  }

  // Render child routes if authenticated
  return <Outlet />;
}
