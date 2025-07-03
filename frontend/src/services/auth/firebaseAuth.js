import { auth, provider, signInWithPopup } from "./firebase";

// Sign in with Google popup, return Firebase JWT token
export async function firebaseSignIn() {
  const result = await signInWithPopup(auth, provider);
  return await result.user.getIdToken(); // Firebase JWT
}
