import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { resolveLocation, updateUserProfile } from "../services/API/profile";
import {
  fetchAllHobbies,
  fetchHobbyCategories,
  getUserHobbies,
  replaceUserHobbies,
} from "../services/API/hobby";
import "./EditProfile.css";

export default function EditProfile({ user, triggerRefresh }) {
  const navigate = useNavigate();
  const [validCategories, setValidCategories] = useState([]);
  const [profilePicFile, setProfilePicFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [resolvedLocation, setResolvedLocation] = useState(null);
  const [showLocationPrompt, setShowLocationPrompt] = useState(false);
  const [allHobbies, setAllHobbies] = useState([]);
  const [userHobbies, setUserHobbies] = useState([]);
  const [selectedHobbyIds, setSelectedHobbyIds] = useState([]);
  const [form, setForm] = useState({
    name: user?.name || "",
    age: user?.age || "",
    bio: user?.bio || "",
    is_private: user?.is_private || false,
    location_id: user?.location?.id || "",
    profile_pic_base64: user?.profile_pic_url || null,
  });
  const [profilePicPreview, setProfilePicPreview] = useState(
    user?.profile_pic_url || ""
  );
  const [searchTerm, setSearchTerm] = useState("");

  const MAX_HOBBIES = 3;
  const userLocation = user?.location;
  const fromSearchSelectedHobbyIds = userHobbies.map((uh) => uh.hobby_id);

  // Filter hobbies by name
  const getOptions = (currentHobbyId) =>
    allHobbies.filter(
      (hobby) =>
        (!fromSearchSelectedHobbyIds.includes(hobby.id) ||
          hobby.id === currentHobbyId) &&
        hobby.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

  // Handle ranked hobby changes
  const handleRankedHobbyChange = (rank, newHobbyId) => {
    const updated = [...userHobbies];
    const existingIndex = updated.findIndex((uh) => uh.rank === rank);
    const existingHobby = updated.find((uh) => uh.hobby_id === newHobbyId);

    // Remove existing hobby if rank changed
    if (existingHobby && existingHobby.rank !== rank) {
      updated.splice(updated.indexOf(existingHobby), 1);
    }

    // Remove existing hobby if newHobbyId is empty
    if (!newHobbyId) {
      if (existingIndex >= 0) {
        updated.splice(existingIndex, 1);
        handleRankUpdate(updated);
      }
      return;
    }

    // Add new hobby
    if (existingIndex >= 0) {
      updated[existingIndex] = {
        ...updated[existingIndex],
        hobby_id: newHobbyId,
      };
    } else {
      updated.push({ id: `temp-${rank}`, hobby_id: newHobbyId, rank });
    }

    // Update state
    handleRankUpdate(updated);
  };

  // Clear ranked hobby
  const clearHobby = (rank) => handleRankedHobbyChange(rank, "");

  // Load hobbies and categories
  useEffect(() => {
    if (!user) return; // user not yet loaded

    let isMounted = true; // for cleanup

    // Load hobbies and categories
    async function loadHobbiesAndCategories() {
      try {
        const [hobbies, categories, existingUserHobbies] = await Promise.all([
          fetchAllHobbies(),
          fetchHobbyCategories(),
          getUserHobbies(),
        ]);

        // Cleanup
        if (!isMounted) return;

        setValidCategories(categories);
        setAllHobbies(hobbies);
        setUserHobbies(existingUserHobbies);
        setSelectedHobbyIds(existingUserHobbies.map((uh) => uh.hobby_id));
      } catch (err) {
        console.error("Error loading hobbies or categories", err);
        if (isMounted) setErrorMsg("Failed to load hobby data.");
      }
    }

    // Initial load
    loadHobbiesAndCategories();

    return () => {
      isMounted = false;
    };
  }, [user]);

  // Input handlers
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // Profile picture
  const handleProfilePicChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== "image/jpeg" && file.type !== "image/png") {
      setErrorMsg("Invalid file type. Please upload a JPEG or PNG file.");
      return;
    }

    // Validate file size
    if (file.size > 2 * 1024 * 1024) {
      setErrorMsg("File size too large. Please choose a smaller file.");
      return;
    }

    // Update state
    setProfilePicFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setProfilePicPreview(reader.result);
    reader.readAsDataURL(file);
  };

  // Convert file to base64
  const fileToBase64 = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result;
        const base64 = result.split(",")[1];

        // Validate base64 length
        if (!base64 || base64.length < 100) {
          console.error("Base64 string too short or invalid", base64);
          reject(new Error("Invalid or incomplete profile picture"));
          return;
        }

        // Update state
        resolve(base64);
      };
      reader.onerror = (e) => {
        console.error("FileReader error", e);
        reject(new Error("Failed to read file"));
      };
      reader.readAsDataURL(file);
    });

  // Location
  const askForLocationPermission = () => setShowLocationPrompt(true);

  // Location prompt
  const handleConfirmLocation = () => {
    setShowLocationPrompt(false);
    detectLocationAndResolve();
  };
  const handleDenyLocation = () => setShowLocationPrompt(false);

  const addNoise = (value, range = 0.05) => {
    const noise = (Math.random() * 2 - 1) * range; // ±range
    return value + noise;
  };

  const roundCoordinate = (value, decimals = 1) => {
    const factor = 10 ** decimals;
    return Math.round(value * factor) / factor;
  };

  const detectLocationAndResolve = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        // Add random noise (~±5km) and round to 1 decimal (~11km accuracy)
        const latitude = roundCoordinate(
          addNoise(position.coords.latitude, 0.05),
          1
        );
        const longitude = roundCoordinate(
          addNoise(position.coords.longitude, 0.05),
          1
        );

        try {
          console.log("Blurred & rounded coordinates:", latitude, longitude);
          const locationData = await resolveLocation(latitude, longitude);
          setResolvedLocation(locationData);
          setForm((prev) => ({ ...prev, location_id: locationData.id }));
        } catch (err) {
          console.error("Location resolve error:", err);
          setErrorMsg("Could not determine location.");
        } finally {
          setLoading(false);
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        setErrorMsg("Location permission denied.");
        setLoading(false);
      }
    );
  };
  

  // Ranked hobbies
  const handleRankUpdate = (updatedHobbies) => {
    setUserHobbies(updatedHobbies);
  };

  // On form submit: update user profile and hobbies by IDs (ranks sorted)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const body = {};
      if (form.name.trim()) body.name = form.name.trim();
      if (form.age !== "" && !isNaN(form.age)) body.age = Number(form.age);
      if (form.bio.trim()) body.bio = form.bio.trim();
      body.is_private = form.is_private;
      if (form.location_id && form.location_id !== "") {
        body.location_id = form.location_id;
      }

      // Profile picture
      if (profilePicFile) {
        const base64 = await fileToBase64(profilePicFile);
        body.profile_pic_base64 = base64;
      }

      // Update profile data first
      await updateUserProfile(body);

      // Prepare hobby IDs sorted by rank for backend PUT /hobbies/me
      if (userHobbies && userHobbies.length > 0) {
        const hobbyIdsInOrder = userHobbies
          .filter(
            (uh) => typeof uh.hobby_id === "string" && uh.hobby_id.trim() !== ""
          )
          .sort((a, b) => a.rank - b.rank)
          .map((uh) => uh.hobby_id);

        console.log("Hobby IDs to send:", hobbyIdsInOrder);
        console.log("Raw user hobbies:", userHobbies);

        await replaceUserHobbies(hobbyIdsInOrder);
      }

      triggerRefresh();
      navigate("/profile");
    } catch (err) {
      console.error("Profile update failed", err);
      setErrorMsg(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="edit-profile-page">
      <h2 className="edit-profile-title">Edit Your Profile</h2>
      <form onSubmit={handleSubmit} noValidate className="edit-profile-form">
        <section>
          {/* Label wraps image to trigger file input on click */}
          <label htmlFor="profile-pic-input">
            {profilePicPreview ? (
              // Show selected image preview
              <img
                src={profilePicPreview}
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
          <label
            htmlFor="profile-pic-input"
            style={{ marginBottom: "0.5rem", display: "block" }}
          >
            Upload a profile picture:
          </label>

          <input
            id="profile-pic-input"
            type="file"
            accept="image/*"
            onChange={handleProfilePicChange}
            style={{ marginBottom: "1rem" }}
            placeholder="Upload a profile picture"
          />
        </section>
        <fieldset className="edit-profile-form">
          {/* Profile Privacy */}
          <label htmlFor="profile-privacy">Profile Privacy:</label>
          <select
            id="profile-privacy"
            name="is_private"
            value={form.is_private ? "private" : "public"}
            onChange={(e) =>
              handleChange({
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

          {/* Name */}
          <label htmlFor="name-input" style={{ marginTop: "1rem" }}>
            Name:
          </label>
          <input
            id="name-input"
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Enter your name"
          />

          {/* Age */}
          <label htmlFor="age-input" style={{ marginTop: "1rem" }}>
            Age:
          </label>
          <input
            id="age-input"
            type="number"
            name="age"
            value={form.age}
            onChange={handleChange}
            placeholder="Enter your age"
          />

          {/* Location */}
          <label htmlFor="age-input" style={{ marginTop: "1rem" }}>
            Location:
          </label>
          <input
            id="age-input"
            type="text"
            name="age"
            readOnly
            value={
              userLocation
                ? [userLocation.city, userLocation.region, userLocation.country]
                    .filter(Boolean)
                    .join(", ")
                : "No location set"
            }
            style={{
              cursor: "not-allowed",
              pointerEvents: "none",
              color: userLocation ? "" : "#888",
            }}
          />

          {/* Bio */}
          <label htmlFor="bio-textarea" style={{ marginTop: "1rem" }}>
            Bio:
          </label>
          <textarea
            id="bio-textarea"
            name="bio"
            value={form.bio}
            onChange={handleChange}
            rows={4}
            placeholder="Tell us about yourself"
          />

          {/* Hobby Selection */}
          <div className="edit-profile-hobbies" style={{ marginTop: "1rem" }}>
            <p className="edit-profile-text-hobbies">
              <label>Select Your Top {MAX_HOBBIES} Hobbies:</label>
            </p>

            {/* Search box */}
            <input
              type="search"
              placeholder="Search hobbies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            {/* Show matching hobbies below search for info only */}
            {searchTerm && (
              <ul
                className="edit-profile-hobby-list"
                aria-label="Search hobbies"
              >
                {allHobbies
                  .filter((hobby) =>
                    hobby.name.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map((hobby) => (
                    <li
                      key={hobby.id}
                      className="edit-profile-hobby-item"
                      tabIndex={-1}
                    >
                      <span>{hobby.name}</span>{" "}
                      <span style={{ fontStyle: "italic", color: "#999" }}>
                        ({hobby.category})
                      </span>
                    </li>
                  ))}
              </ul>
            )}

            {/* Current selected hobbies with dropdowns */}
            {[...Array(MAX_HOBBIES)].map((_, i) => {
              const rank = i + 1;
              const current = userHobbies.find((uh) => uh.rank === rank);
              const currentHobbyId = current?.hobby_id || "";

              return (
                <div
                  key={rank}
                  style={{
                    marginTop: "1rem",
                    marginBottom: "0.8rem",
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  <label
                    htmlFor={`rank-${rank}`}
                    style={{ flexShrink: 0, minWidth: "85px" }}
                  >
                    Rank {rank} Hobby:
                  </label>
                  <select
                    id={`rank-${rank}`}
                    value={currentHobbyId}
                    onChange={(e) =>
                      handleRankedHobbyChange(rank, e.target.value)
                    }
                    style={{ flexGrow: 1, marginLeft: "0.5rem" }}
                  >
                    <option value="">-- Select a hobby --</option>
                    {getOptions(currentHobbyId).map((hobby) => (
                      <option key={hobby.id} value={hobby.id}>
                        {hobby.name} ({hobby.category})
                      </option>
                    ))}
                  </select>

                  {/* Clear button */}
                  {currentHobbyId && (
                    <button
                      type="button"
                      onClick={() => clearHobby(rank)}
                      className="hobby-clear-btn"
                      aria-label={`Clear hobby for rank ${rank}`}
                      style={{ marginLeft: "1rem" }}
                    >
                      ❌
                    </button>
                  )}
                </div>
              );
            })}

            {errorMsg && (
              <p
                className="error-msg"
                style={{ marginTop: "1rem", color: "#ff5555" }}
              >
                {errorMsg}
              </p>
            )}
          </div>
        </fieldset>
        {resolvedLocation && (
          // Display resolved location
          <div className="location-display" style={{ marginTop: "1rem" }}>
            <strong style={{ color: "green" }}>Location detected </strong>
            <p>
              {resolvedLocation.city}, {resolvedLocation.region},{" "}
              {resolvedLocation.country}
            </p>
          </div>
        )}
        {!showLocationPrompt && (
          // Location buttons
          <div
            style={{
              display: "flex",
              gap: "1rem",
              marginTop: "0.5rem",
              flexWrap: "wrap",
              width: "100%",
            }}
            className="location-section"
          >
            {/* Button to request current location */}
            <button
              type="button"
              className="location-button btn btn-secondary"
              onClick={askForLocationPermission}
              disabled={loading}
            >
              📍 Use My Current Location
            </button>

            {/* Submit button with loading state */}
            <button
              type="submit"
              className="btn primary-btn"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save and Continue"}
            </button>

            {/* Cancel button */}
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate("/profile")}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        )}
        {showLocationPrompt && (
          // Prompt container with message and buttons
          <div className="location-prompt">
            <p>
              Do you want to share your location to auto-fill city, state, and
              country?
            </p>
            <div className="location-prompt-buttons">
              {/* Confirm sharing location */}
              <button
                className="btn primary-btn"
                onClick={handleConfirmLocation}
              >
                Yes, share location
              </button>

              {/* Deny sharing location */}
              <button
                className="btn btn-secondary"
                onClick={handleDenyLocation}
              >
                No, thanks
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
