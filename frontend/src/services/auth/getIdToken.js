import { auth } from "../auth/firebase";

/**
 * Helper: Get Firebase ID token from current user.
 * @returns {Promise<string>} Firebase ID token.
 */
export async function getIdToken() {
  const currentUser = auth.currentUser;
  if (!currentUser) throw new Error("User not logged in");
  return await currentUser.getIdToken(true);
}
