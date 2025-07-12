
const KEY = "authUser"; // Key used to store auth data in localStorage

/**
 * Save authentication data (user info and token) to localStorage.
 * Stores data as a JSON string under a specific key.
 * 
 * @param {Object} userData - The user data to save (e.g., { user, token }).
 */
export function saveAuthUser(userData) {
  localStorage.setItem(KEY, JSON.stringify(userData));
}

/**
 * Load authentication data from localStorage.
 * Parses the stored JSON string back into an object.
 * Returns null if no data is found.
 * 
 * @returns {Object|null} The stored auth data or null if not found.
 */
export function loadAuthUser() {
  const stored = localStorage.getItem(KEY);
  return stored ? JSON.parse(stored) : null;
}

/**
 * Clear authentication data from localStorage.
 * Removes the stored auth data key.
 */
export function clearAuthUser() {
  localStorage.removeItem(KEY);
}
