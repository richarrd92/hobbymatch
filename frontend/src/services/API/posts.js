import { auth } from "../auth/firebase";

const BASE_URL = "http://localhost:8000";
const POSTS_URL = `${BASE_URL}/posts`;

// Get Firebase user token for auth headers
async function getIdToken() {
  const currentUser = auth.currentUser;
  if (!currentUser) throw new Error("User not logged in");
  const token = await currentUser.getIdToken(true);
  return token;
}

// Create a new post (optional image + hobby)
export async function createPost({
  content,
  hobby_id = null,
  imageFile = null,
}) {
  const idToken = await getIdToken();
  const formData = new FormData();

  // Append form data
  formData.append("content", String(content));
  if (hobby_id) formData.append("hobby_id", String(hobby_id));
  if (imageFile instanceof File) formData.append("file", imageFile);
  
  // Send request
  const res = await fetch(POSTS_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${idToken}`,
      // No need to manually set 'Content-Type' when using FormData
    },
    body: formData,
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to create post");
  }

  return await res.json();
}

// Fetch public feed posts
export async function fetchPublicFeed() {
  const res = await fetch(`${POSTS_URL}/feed`);
  if (!res.ok) throw new Error("Failed to fetch feed");
  return await res.json();
}

// Post a comment on a given post
export async function addComment(postId, content) {
  const idToken = await getIdToken();

  // Send request
  const res = await fetch(`${POSTS_URL}/${postId}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ content }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to add comment");
  }

  return await res.json();
}

// React to a post (e.g., like, love, etc.)
export async function reactToPost(postId, reactionType) {
  const idToken = await getIdToken();

  // Send request
  const res = await fetch(`${POSTS_URL}/${postId}/reactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ type: reactionType }),
  });

  // Throw error if response not ok
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to add reaction");
  }

  return await res.json();
}
