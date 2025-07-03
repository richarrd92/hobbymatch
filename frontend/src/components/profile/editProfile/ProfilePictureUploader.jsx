import "./ProfilePictureUploader.css";

// Handles profile picture upload and preview display
export default function ProfilePictureUploader({ preview, onChange }) {
  return (
    <section>
      {/* Label wraps image to trigger file input on click */}
      <label htmlFor="profile-pic-input">
        {preview ? (
          // Show selected image preview
          <img
            src={preview}
            alt="Profile Preview"
            className="profile-preview"
            title="Click to Change Profile Picture"
          />
        ) : (
          // Show default avatar if no preview is set
          <img
            src="/default-avatar.png"
            alt="Avatar"
            className="profile-preview"
            title="Click to Change Profile Picture"
          />
        )}
      </label>

      {/* Hidden file input triggered by image click */}
      <input
        id="profile-pic-input"
        type="file"
        accept="image/*"
        onChange={onChange}
        style={{ display: "none" }}
      />
    </section>
  );
}
