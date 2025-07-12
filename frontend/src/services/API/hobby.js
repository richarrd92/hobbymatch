import { getIdToken } from "../auth/getIdToken";

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


/**
 * Fetch public list of hobby categories.
 * @returns {Promise<string[]>} Array of category names.
 */
export async function fetchHobbyCategories() {
  const response = await fetch(`${HOBBIES_URL}/categories`);
  if (!response.ok) throw new Error("Failed to fetch hobby categories");
  return await response.json();
}

/**
 * Fetch all hobbies (public).
 * @returns {Promise<object[]>} Array of hobby objects.
 */
export async function fetchAllHobbies() {
  const response = await fetch(HOBBIES_URL);
  if (!response.ok) throw new Error("Failed to fetch hobbies");
  return await response.json();
}

/**
 * Get the current user's selected hobbies.
 * Requires user to be authenticated.
 * @returns {Promise<object[]>} Array of user's hobby objects.
 */
export async function getUserHobbies() {
  const idToken = await getIdToken();
  const response = await fetch(USER_HOBBIES_GET_URL, {
    headers: { Authorization: `Bearer ${idToken}` },
  });

  // Throw error if response not ok
  if (!response.ok) throw new Error("Failed to fetch user hobbies");
  return await response.json();
}

/**
 * Replace the user's hobbies using full hobby objects.
 * @param {object[]} hobbyObjs - Array of { name, category } objects.
 * @returns {Promise<object[]>} Updated hobbies.
 */
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
  const response = await fetch(USER_HOBBIES_GET_URL, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(hobbyObjs),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(
      errData.detail || "Failed to replace user hobbies with objects"
    );
  }

  return await response.json();
}

/**
 * Replace the user's hobbies using an array of hobby IDs.
 * @param {string[]} hobbyIds - Array of hobby ID strings.
 * @returns {Promise<object[]>} Updated hobbies.
 */
export async function replaceUserHobbies(hobbyIds) {
  if (!Array.isArray(hobbyIds)) throw new Error("Input must be an array");
  if (hobbyIds.length > 3) {
    throw new Error("You can select up to 3 hobbies only");
  }

  // Send request
  const idToken = await getIdToken();
  const response = await fetch(USER_HOBBIES_PUT_URL, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ hobby_ids: hobbyIds }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    console.error("422 validation error details:", errData);
    throw new Error(errData.detail || "Failed to replace user hobbies");
  }

  return await response.json();
}

/**
 * Admin: Create a new hobby.
 * @param {string} name - Name of the new hobby.
 * @param {string} category - Valid category name.
 * @returns {Promise<object>} Created hobby object.
 */
export async function createHobby(name, category) {
  if (!VALID_CATEGORIES.includes(category)) {
    throw new Error(`Invalid category: ${category}`);
  }

  // Send request
  const idToken = await getIdToken();
  const response = await fetch(HOBBIES_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ name: name.trim(), category }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to create hobby");
  }

  return await response.json();
}

/**
 * Admin: Update an existing hobby.
 * @param {string} hobbyId - ID of the hobby to update.
 * @param {string} name - New name for the hobby.
 * @param {string|null} category - Optional new category.
 * @returns {Promise<object>} Updated hobby object.
 */
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
  const response = await fetch(`${HOBBIES_URL}/${hobbyId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(body),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to update hobby");
  }

  return await response.json();
}

/**
 * Admin: Delete a hobby by ID.
 * @param {string} hobbyId - ID of the hobby to delete.
 * @returns {Promise<boolean>} True if successful.
 */
export async function deleteHobby(hobbyId) {
  const idToken = await getIdToken();

  // Send request
  const response = await fetch(`${HOBBIES_URL}/${hobbyId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${idToken}` },
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to delete hobby");
  }

  return true;
}

/**
 * Fetch a single hobby by ID (public).
 * @param {string} hobbyId - Hobby ID to fetch.
 * @returns {Promise<object>} Hobby object.
 */
export async function fetchHobbyById(hobbyId) {
  const response = await fetch(`${HOBBIES_URL}/${hobbyId}`);
  if (!response.ok) throw new Error("Failed to fetch hobby by ID");
  return await response.json();
}