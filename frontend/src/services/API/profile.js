import { getIdToken } from "../auth/getIdToken";

/**
 * Resolve latitude and longitude to a human-readable location using backend service.
 * Requires authentication.
 * 
 * @param {number} latitude - Latitude coordinate.
 * @param {number} longitude - Longitude coordinate.
 * @returns {Promise<object>} Location data including city, state, etc.
 */
export async function resolveLocation(latitude, longitude) {
  const idToken = await getIdToken();

  // Send request
  const response = await fetch("http://localhost:8000/locations/resolve", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ latitude, longitude }),
  });

  // Throw error if response not ok
  if (!response.ok) throw new Error("Failed to resolve location");

  return await response.json();
}

/**
 * Update the current user's profile via backend PATCH request.
 * Requires authentication.
 * 
 * @param {object} profileData - Partial user profile data (e.g., name, location).
 * @returns {Promise<object>} Updated user profile data.
 */
export async function updateUserProfile(profileData) {
  const idToken = await getIdToken();

  // Send request
  const response = await fetch("http://localhost:8000/users/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(profileData),
  });

  // Parse error details from response if update fails
  if (!response.ok) {
    const errData = await response.json();
    throw new Error(
      Array.isArray(errData.detail)
        ? errData.detail.map((e) => e.msg).join(", ")
        : errData.detail || "Update failed"
    );
  }

  return await response.json();
}
