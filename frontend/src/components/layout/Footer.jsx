import "./Footer.css";

// Footer component
export default function Footer() {
  return (
    <footer className="footer-bar">
      <p className="footer-text">
        © 2025 HobbyMatch &nbsp;·&nbsp; {/* Copyright notice */}
        <a href="#">About</a> &nbsp;·&nbsp;
        <a href="#">Help</a> &nbsp;·&nbsp;
        <a href="#">Privacy</a>
      </p>
    </footer>
  );
}
