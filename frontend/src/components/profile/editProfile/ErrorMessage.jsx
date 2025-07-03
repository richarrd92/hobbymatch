// Renders an error message if one exists
export default function ErrorMessage({ message }) {
  // Do not render anything if there's no message
  if (!message) return null;

  return (
    // Styled error text
    <p className="error-msg" style={{ marginTop: "1rem", color: "#ff5555" }}>
      {message}
    </p>
  );
}
