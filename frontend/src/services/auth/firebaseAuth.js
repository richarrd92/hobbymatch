import { auth, provider, signInWithPopup } from "./firebase";

/**
 * Initiates Google Sign-In using a popup window.
 *
 * @returns {Promise<string>} Firebase JWT token (ID token) for authenticated user
 * @throws Will propagate any sign-in errors (e.g., popup blocked, auth denied)
 */
export async function firebaseSignIn() {
  try {
    const result = await signInWithPopup(auth, provider); // Triggers Google Sign-In popup
    return await result.user.getIdToken(); // Retrieves Firebase ID token (JWT)
  } catch (error) {
    console.error("Firebase sign-in failed:", error);
    throw error; // Propagate error to caller
  }
}
