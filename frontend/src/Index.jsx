import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./services/auth/AuthProvider";

/**
 * Entry point of the React application.
 *
 * Renders the root component <App /> wrapped inside <AuthProvider> to provide
 * authentication context to the entire app.
 *
 * This ensures that all child components have access to auth state and methods.
 */
ReactDOM.createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
 