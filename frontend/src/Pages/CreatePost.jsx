import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAllHobbies } from "../services/API/hobby";
import { createPost } from "../services/API/posts";
import "./CreatePost.css";

export default function CreatePost() {
  const navigate = useNavigate();

  // State to hold hobby list, loading state, and error messages
  const [allHobbies, setAllHobbies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Form data for content and selected hobby
  const [form, setForm] = useState({
    content: "",
    hobby_id: "",
  });

  // Image file and preview state
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");

  // Fetch hobbies on mount
  useEffect(() => {
    fetchAllHobbies()
      .then(setAllHobbies)
      .catch((err) => {
        console.error("Failed to load hobbies", err);
        setErrorMsg("Could not load hobbies.");
      });
  }, []);

  // Update form input values
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  // Validate and preview uploaded image
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setErrorMsg("Only JPEG or PNG files are allowed.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg("Max file size is 5MB.");
      return;
    }

    setImageFile(file);
    setErrorMsg("");

    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  // Submit form and create post
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.content.trim()) {
      setErrorMsg("Caption is required.");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    try {
      // Create post
      await createPost({
        content: form.content.trim(),
        hobby_id: form.hobby_id || null,
        imageFile,
      });
      navigate("/feed"); // Redirect after success
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Failed to create post.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-page">
      <h2>Create a New Post</h2>
      <form className="create-post-form" onSubmit={handleSubmit} noValidate>
        {/* Post content */}
        <label>Caption:</label>
        <textarea
          name="content"
          rows="4"
          value={form.content}
          onChange={handleChange}
          placeholder="What's on your mind?"
          required
        />
        {/* Optional hobby tag */}
        <label style={{ marginTop: "1rem" }}>Tag a Hobby (optional):</label>
        <select name="hobby_id" value={form.hobby_id} onChange={handleChange}>
          <option value="">-- None --</option>
          {allHobbies.map((hobby) => (
            <option key={hobby.id} value={hobby.id}>
              {hobby.name}
            </option>
          ))}
        </select>
        {/* Optional image upload */}
        <label style={{ marginTop: "1rem" }}>Image (optional):</label>
        <input
          type="file"
          accept="image/jpeg,image/png"
          onChange={handleImageChange}
        />
        {imagePreview && (
          <img
            src={imagePreview}
            alt="Preview"
            className="image-preview"
            style={{ marginTop: "1rem", maxWidth: "100%", borderRadius: "8px" }}
          />
        )}
        {/* Error message */}
        {errorMsg && (
          <p className="error-msg" style={{ color: "red", marginTop: "1rem" }}>
            {errorMsg}
          </p>
        )}

        {/* Submit and cancel buttons */}
        <div style={{ marginTop: "1rem" }}>
          <button type="submit" disabled={loading}>
            {loading ? "Posting..." : "Create Post"}
          </button>
          <button
            type="button"
            style={{ marginLeft: "1rem" }}
            onClick={() => navigate("/feed")}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
