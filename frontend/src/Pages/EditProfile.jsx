import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ProfilePictureUploader from "../components/profile/editProfile/ProfilePictureUploader";
import BasicInfoForm from "../components/profile/editProfile/BasicInfoForm";
import LocationPrompt from "../components/profile/editProfile/LocationPrompt";
import DetectedLocationDisplay from "../components/profile/editProfile/DetectedLocationDisplay";
import PhotosGridPlaceholder from "../components/profile/PhotosGridPlaceholder";
import FormButtons from "../components/profile/editProfile/FormButtons";
import ErrorMessage from "../components/profile/editProfile/ErrorMessage";
import { resolveLocation, updateUserProfile } from "../services/API/profileAPI";
import "./EditProfile.css";

// Form to edit user profile with photo upload, location detection, and basic info
export default function EditProfile({ user, triggerRefresh }) {
  const navigate = useNavigate();

  // Form state initialized from user prop
  const [form, setForm] = useState({
    name: user?.name || "",
    age: user?.age || "",
    bio: user?.bio || "",
    is_private: user?.is_private || false,
    location_id: user?.location?.id || "",
    profile_pic_base64: user?.profile_pic_url || null,
  });

  // Profile picture preview and selected file state
  const [profilePicPreview, setProfilePicPreview] = useState(
    user?.profile_pic_url || ""
  );
  const [profilePicFile, setProfilePicFile] = useState(null);

  // Loading and error message state
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Location-related states
  const [resolvedLocation, setResolvedLocation] = useState(null);
  const [showLocationPrompt, setShowLocationPrompt] = useState(false);

  // Handle input changes for form fields
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // Handle profile picture file selection and preview update
  const handleProfilePicChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setProfilePicFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setProfilePicPreview(reader.result);
    reader.readAsDataURL(file);
  };

  // Convert file to base64 string for upload
  const fileToBase64 = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  // Show location permission prompt
  const askForLocationPermission = () => setShowLocationPrompt(true);

  // Confirm location sharing and fetch location
  const handleConfirmLocation = () => {
    setShowLocationPrompt(false);
    detectLocationAndResolve();
  };

  // Deny location sharing
  const handleDenyLocation = () => setShowLocationPrompt(false);

  // Detect user location via browser and resolve it via API
  const detectLocationAndResolve = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
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

  // Submit updated profile to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const body = {};

      if (form.name && form.name.trim() !== "") body.name = form.name.trim();
      if (form.age !== "" && form.age !== null && !isNaN(form.age))
        body.age = Number(form.age);
      if (form.bio && form.bio.trim() !== "") body.bio = form.bio.trim();

      body.is_private = form.is_private;
      if (form.location_id && form.location_id !== "")
        body.location_id = form.location_id;

      if (profilePicFile) {
        const base64 = await fileToBase64(profilePicFile);
        body.profile_pic_base64 = base64;
      }

      await updateUserProfile(body);

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
        {/* Profile picture uploader */}
        <ProfilePictureUploader
          preview={profilePicPreview}
          onChange={handleProfilePicChange}
          style={{ justifyContent: "center" }}
        />

        {/* Basic info inputs */}
        <BasicInfoForm form={form} onChange={handleChange} />

        {/* Show detected location if available */}
        {resolvedLocation && (
          <DetectedLocationDisplay location={resolvedLocation} />
        )}

        {/* Placeholder for future photos feature */}
        <PhotosGridPlaceholder />

        {/* Location-related buttons and prompt */}
        <section className="location-section">
          {!showLocationPrompt && (
            <FormButtons
              loading={loading}
              onRequestLocation={askForLocationPermission}
              onCancel={() => navigate("/profile")}
            />
          )}
          <LocationPrompt
            visible={showLocationPrompt}
            onConfirm={handleConfirmLocation}
            onDeny={handleDenyLocation}
          />
        </section>

        {/* Display error messages */}
        <ErrorMessage message={errorMsg} />
      </form>
    </div>
  );
}
