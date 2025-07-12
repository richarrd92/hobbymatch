import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from "firebase/auth";

/**
 * Firebase configuration loaded from environment variables.
 * Keep API keys secure and hidden via Vite env vars (prefix with VITE_).
 */
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

/**
 * Initializes the Firebase application using the provided config.
 * Also sets up Firebase Authentication with Google Sign-In.
 */
const app = initializeApp(firebaseConfig);     // Firebase app instance
const auth = getAuth(app);                     // Firebase Auth service
const provider = new GoogleAuthProvider();     // Google sign-in provider

/**
 * Exported tools:
 * - `auth`: for accessing the current user and auth state
 * - `provider`: GoogleAuthProvider instance
 * - `signInWithPopup`: to trigger sign-in via Google
 * - `signOut`: to log the user out
 */
export { auth, provider, signInWithPopup, signOut };