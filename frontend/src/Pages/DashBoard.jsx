import { Outlet } from "react-router-dom";
import "./Dashboard.css";

// Dashboard wrapper with layout
export default function Dashboard({ topBar, sideBar, footer }) {
  return (
    <div className="home-page">
      {topBar}
      {sideBar}
      <main style={{ overflowY: "auto" }}>
        <Outlet /> {/* Nested route content renders here */}
      </main>
      {footer}
    </div>
  );
}
