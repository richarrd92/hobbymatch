import "./LocationPrompt.css";

// Prompts the user for permission to access their location
export default function LocationPrompt({ visible, onConfirm, onDeny }) {
  // Don't render the prompt if it's not visible
  if (!visible) return null;

  return (
    // Prompt container with message and buttons
    <div className="location-prompt">
      <p>
        Do you want to share your location to auto-fill city, state, and
        country?
      </p>
      <div className="location-prompt-buttons">
        {/* Confirm sharing location */}
        <button className="btn primary-btn" onClick={onConfirm}>
          Yes, share location
        </button>

        {/* Deny sharing location */}
        <button className="btn btn-secondary" onClick={onDeny}>
          No, thanks
        </button>
      </div>
    </div>
  );
}
