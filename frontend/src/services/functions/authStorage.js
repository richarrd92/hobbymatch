// Handles saving, loading, and clearing auth data in localStorage

const KEY = "authUser";

// Save user data (user + token) as JSON string
export function saveAuthUser(userData) {
  localStorage.setItem(KEY, JSON.stringify(userData));
}

// Load user data from localStorage, parse JSON or return null
export function loadAuthUser() {
  const stored = localStorage.getItem(KEY);
  return stored ? JSON.parse(stored) : null;
}

// Remove auth data from localStorage
export function clearAuthUser() {
  localStorage.removeItem(KEY);
}
