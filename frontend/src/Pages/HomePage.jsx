import { Outlet, Navigate } from "react-router-dom";
import Dashboard from "./DashBoard";
import NavBar from "./NavBar";
import SideBar from "./SideBar";
import Footer from "./Footer";

// Main layout wrapping dashboard, navigation, sidebar, and footer
export default function HomePage({ user }) {
  // Redirect to login if user not logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Dashboard
      topBar={<NavBar user={user} />}
      sideBar={<SideBar />}
      footer={<Footer />}
    >
      {/* Render child routes here */}
      <Outlet />
    </Dashboard>
  );
}
