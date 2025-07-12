const BASE_URL = "http://localhost:8000/auth"; 

/**
 * Logs in a user by sending the Firebase ID token to the backend.
 *
 * @param {string} idToken - Firebase-issued ID token for the signed-in user.
 * @returns {Promise<object>} - Resolves to user data returned by backend.
 * @throws {Error} - Throws an error if login fails or response is not OK.
 */
export async function backendLogin(idToken) {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const error = new Error("Login failed");
    error.status = response.status;
    throw error;
  }

  return response.json();
}

/**
 * Signs up a new user by sending the Firebase ID token to the backend.
 *
 * @param {string} idToken - Firebase-issued ID token from client.
 * @returns {Promise<object>} - Resolves to newly created user data.
 * @throws {Error} - Throws an error if signup fails or response is not OK.
 */
export async function backendSignup(idToken) {
  const response = await fetch(`${BASE_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const error = new Error("Signup failed");
    error.status = response.status;
    throw error;
  }

  return response.json();
}
