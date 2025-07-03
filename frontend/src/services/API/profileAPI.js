// API calls that require Firebase auth token for authorization

import { auth } from "../auth/firebase";

// Get fresh Firebase ID token or throw if no user
async function getIdToken() {
  const currentUser = auth.currentUser;
  if (!currentUser) throw new Error("User not logged in");
  return await currentUser.getIdToken(true);
}

// Resolve latitude/longitude to location info via backend
export async function resolveLocation(latitude, longitude) {
  const idToken = await getIdToken();

  const res = await fetch("http://localhost:8000/locations/resolve", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ latitude, longitude }),
  });

  if (!res.ok) throw new Error("Failed to resolve location");

  return await res.json();
}

// Update current user's profile data via backend PATCH
export async function updateUserProfile(profileData) {
  const idToken = await getIdToken();

  const res = await fetch("http://localhost:8000/users/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(profileData),
  });

  // Parse error details from response if update fails
  if (!res.ok) {
    const errData = await res.json();
    throw new Error(
      Array.isArray(errData.detail)
        ? errData.detail.map((e) => e.msg).join(", ")
        : errData.detail || "Update failed"
    );
  }

  return await res.json();
}
