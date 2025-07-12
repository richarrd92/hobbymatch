import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAllHobbies } from "../services/API/hobby";
import { createPost } from "../services/API/posts";
import "./CreatePost.css";

/**
 * CreatePost component allows users to create a new post with optional image
 * and hobby association. It manages form state, handles input changes, image
 * validation, and submits the post data to the backend. Redirects to the feed
 * on successful submission.
 *
 * @returns {JSX.Element} The UI for creating a new post with form fields for
 * caption, hobby tag, and image upload, including error handling and loading states.
 */
export default function CreatePost() {
  const navigate = useNavigate();

  // State to hold hobby list, loading state, and error messages
  const [allHobbies, setAllHobbies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  /**
   * @typedef {Object} PostForm
   * @property {string} content - The caption content of the post
   * @property {string} hobby_id - The ID of the selected hobby (optional)
   * @type {[PostForm, Function]} The post form input values
   */
  const [form, setForm] = useState({
    content: "",
    hobby_id: "",
  });

  // Image file and preview state
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");

  /**
   * Fetch all hobbies once when component mounts.
   * Sets hobby options for the hobby select dropdown.
   */
  useEffect(() => {
    fetchAllHobbies()
      .then(setAllHobbies)
      .catch((err) => {
        console.error("Failed to load hobbies", err);
        setErrorMsg("Could not load hobbies.");
      });
  }, []);

  /**
   * Handles changes to form input fields.
   * @param {React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>} e
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  /**
   * Handles image selection, validates type and size,
   * and sets preview using FileReader.
   * @param {React.ChangeEvent<HTMLInputElement>} e
   */
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setErrorMsg("Only JPEG or PNG files are allowed.");
      return;
    }

    // Validate file size
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg("Max file size is 5MB.");
      return;
    }

    // Update state
    setImageFile(file);
    setErrorMsg("");

    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  /**
   * Submits the post form.
   * Sends content, hobby ID, and image (if any) to the backend.
   * Redirects to /feed on success.
   * @param {React.FormEvent<HTMLFormElement>} e
   */
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
