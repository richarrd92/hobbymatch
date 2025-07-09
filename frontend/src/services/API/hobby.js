import { auth } from "../auth/firebase";

const BASE_URL = "http://localhost:8000";
const HOBBIES_URL = `${BASE_URL}/hobbies`;
const USER_HOBBIES_GET_URL = `${HOBBIES_URL}/users/me/hobbies`;
const USER_HOBBIES_PUT_URL = `${HOBBIES_URL}/me`;

const VALID_CATEGORIES = [
  "Sports",
  "Outdoors",
  "Creative",
  "Music",
  "Culinary",
  "Crafts",
  "Tech",
  "Games",
  "Lifestyle",
  "Wellness",
  "Fitness",
  "Entertainment",
  "Nature",
  "Finance",
  "Community",
  "Academic",
];

// Helper: Get Firebase ID Token for Authorization
async function getIdToken() {
  const currentUser = auth.currentUser;
  if (!currentUser) throw new Error("User not logged in");
  return await currentUser.getIdToken(true);
}

// Hobby Categories (public)
export async function fetchHobbyCategories() {
  const res = await fetch(`${HOBBIES_URL}/categories`);
  if (!res.ok) throw new Error("Failed to fetch hobby categories");
  return await res.json();
}

// All Hobbies (public)
export async function fetchAllHobbies() {
  const res = await fetch(HOBBIES_URL);
  if (!res.ok) throw new Error("Failed to fetch hobbies");
  return await res.json();
}

// User Hobbies - get current user's hobbies
export async function getUserHobbies() {
  const idToken = await getIdToken();
  const res = await fetch(USER_HOBBIES_GET_URL, {
    headers: { Authorization: `Bearer ${idToken}` },
  });

  // Throw error if response not ok
  if (!res.ok) throw new Error("Failed to fetch user hobbies");
  return await res.json();
}

// User Hobbies - replace current user's hobbies with array of hobby objects
// Endpoint: PUT /hobbies/users/me/hobbies
// Input: array of {name: string, category: string}
export async function replaceUserHobbiesWithObjects(hobbyObjs) {
  if (!Array.isArray(hobbyObjs)) throw new Error("Input must be an array");
  if (hobbyObjs.length > 3) {
    throw new Error("You can select up to 3 hobbies only");
  }

  // Validate categories in hobby objects
  for (const h of hobbyObjs) {
    if (!VALID_CATEGORIES.includes(h.category)) {
      throw new Error(`Invalid category: ${h.category}`);
    }
  }

  // Send request
  const idToken = await getIdToken();
  const res = await fetch(USER_HOBBIES_GET_URL, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(hobbyObjs),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(
      errData.detail || "Failed to replace user hobbies with objects"
    );
  }

  return await res.json();
}

// User Hobbies - replace current user's hobbies with array of hobby IDs
// Endpoint: PUT /hobbies/me
// Input: { hobby_ids: string[] }
export async function replaceUserHobbies(hobbyIds) {
  if (!Array.isArray(hobbyIds)) throw new Error("Input must be an array");
  if (hobbyIds.length > 3) {
    throw new Error("You can select up to 3 hobbies only");
  }

  // Send request
  const idToken = await getIdToken();
  const res = await fetch(USER_HOBBIES_PUT_URL, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ hobby_ids: hobbyIds }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    console.error("422 validation error details:", errData);
    throw new Error(errData.detail || "Failed to replace user hobbies");
  }

  return await res.json();
}

// Admin: create a new hobby
export async function createHobby(name, category) {
  if (!VALID_CATEGORIES.includes(category)) {
    throw new Error(`Invalid category: ${category}`);
  }

  // Send request
  const idToken = await getIdToken();
  const res = await fetch(HOBBIES_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ name: name.trim(), category }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to create hobby");
  }

  return await res.json();
}

// Admin: update existing hobby by id
export async function updateHobby(hobbyId, name, category = null) {
  const idToken = await getIdToken();

  // Validate category
  const body = { name: name.trim() };
  if (category) {
    if (!VALID_CATEGORIES.includes(category)) {
      throw new Error(`Invalid category: ${category}`);
    }
    body.category = category;
  }

  // Send request
  const res = await fetch(`${HOBBIES_URL}/${hobbyId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(body),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to update hobby");
  }

  return await res.json();
}

// Admin: delete hobby by id
export async function deleteHobby(hobbyId) {
  const idToken = await getIdToken();

  // Send request
  const res = await fetch(`${HOBBIES_URL}/${hobbyId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${idToken}` },
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to delete hobby");
  }

  return true;
}

// Fetch hobby by ID (public)
export async function fetchHobbyById(hobbyId) {
  const res = await fetch(`${HOBBIES_URL}/${hobbyId}`);
  if (!res.ok) throw new Error("Failed to fetch hobby by ID");
  return await res.json();
}