// API calls for backend login and signup using Firebase ID token

const BASE_URL = "http://localhost:8000/auth";

// Login: send ID token, receive user data or error
export async function backendLogin(idToken) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const error = new Error("Login failed");
    error.status = res.status;
    throw error;
  }

  return res.json();
}

// Signup: send ID token, receive new user data or error
export async function backendSignup(idToken) {
  const res = await fetch(`${BASE_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const error = new Error("Signup failed");
    error.status = res.status;
    throw error;
  }

  return res.json();
}
