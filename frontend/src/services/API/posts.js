import { getIdToken } from "../auth/getIdToken";

const BASE_URL = "http://localhost:8000";
const POSTS_URL = `${BASE_URL}/posts`;

/**
 * Create a new post with optional image and hobby association.
 * @param {object} params
 * @param {string} params.content - Text caption content of the post.
 * @param {string|null} [params.hobby_id] - Optional hobby ID.
 * @param {File|null} [params.imageFile] - Optional image file.
 * @returns {Promise<object>} Created post object.
 */
export async function createPost({
  content,
  hobby_id = null,
  imageFile = null,
}) {
  const idToken = await getIdToken();
  const formData = new FormData();

  // Add fields to form data
  formData.append("content", String(content));
  if (hobby_id) formData.append("hobby_id", String(hobby_id));
  if (imageFile instanceof File) formData.append("file", imageFile);

  // Send request
  const response = await fetch(POSTS_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${idToken}`,
      // Content-Type automatically handled by FormData
    },
    body: formData,
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to create post");
  }

  return await response.json();
}

/**
 * Fetch the public feed of posts.
 * @returns {Promise<object[]>} Array of public post objects.
 */
export async function fetchPublicFeed() {
  const response = await fetch(`${POSTS_URL}/feed`);
  if (!response.ok) throw new Error("Failed to fetch feed");
  return await response.json();
}

/**
 * Add a comment to a specific post.
 * @param {string} postId - ID of the post to comment on.
 * @param {string} content - Comment text.
 * @returns {Promise<object>} Created comment object.
 */
export async function addComment(postId, content) {
  const idToken = await getIdToken();

  // Send request
  const response = await fetch(`${POSTS_URL}/${postId}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ content }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to add comment");
  }

  return await response.json();
}

/**
 * React to a specific post (e.g., like, love, etc.).
 * @param {string} postId - ID of the post to react to.
 * @param {string} reactionType - Type of reaction (e.g., "like", "love").
 * @returns {Promise<object>} Created reaction object.
 */
export async function reactToPost(postId, reactionType) {
  const idToken = await getIdToken();

  // Send request
  const response = await fetch(`${POSTS_URL}/${postId}/reactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ type: reactionType }),
  });

  // Throw error if response not ok
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to add reaction");
  }

  return await response.json();
}
