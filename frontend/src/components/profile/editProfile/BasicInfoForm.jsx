import "./BasicInfoForm.css";

// Renders a form for editing basic user profile information
export default function BasicInfoForm({ form, onChange }) {
  return (
    <fieldset className="edit-profile-form">
      {/* Profile visibility selection */}
      <label className="checkbox-label" style={{ marginTop: "1rem" }}>
        Profile Privacy:
        <select
          name="is_private"
          value={form.is_private ? "private" : "public"}
          onChange={(e) =>
            onChange({
              target: {
                name: "is_private",
                value: e.target.value === "private",
              },
            })
          }
        >
          <option value="public">Public</option>
          <option value="private">Private</option>
        </select>
      </label>

      {/* Name input field */}
      <label>
        Name:
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={onChange}
          placeholder="Enter your name"
          style={{ marginTop: "0.3rem" }}
        />
      </label>

      {/* Age input field */}
      <label>
        Age:
        <input
          type="number"
          name="age"
          value={form.age}
          onChange={onChange}
          min={0}
          max={120}
          placeholder="Enter your age"
          style={{ marginTop: "0.3rem" }}
        />
      </label>

      {/* Bio text area */}
      <label style={{ marginTop: "1rem" }}>
        Bio:
        <textarea
          name="bio"
          value={form.bio}
          onChange={onChange}
          placeholder="Tell us about yourself"
          rows={4}
          style={{ marginTop: "0.3rem" }}
        />
      </label>
    </fieldset>
  );
}
