/**
 * Creates a WebSocket connection to the feed endpoint for real-time updates.
 *
 * @param {string} token - Firebase authentication token for user authorization.
 * @param {Object} handlers - Object containing handler functions for feed updates.
 * @param {function} handlers.setPosts - Function to update the list of posts in state.
 * @param {function} handlers.refreshPostById - Function to refresh a single post by its ID.
 *
 * @returns {WebSocket} The WebSocket instance connected to the feed.
 *
 * @description
 * Establishes a WebSocket connection to receive real-time feed events such as new posts,
 * comments, reactions, and post deletions. Updates are applied via the provided handler functions.
 */
export function createFeedWebSocket(token, { setPosts, refreshPostById }) {
  const socket = new WebSocket(`ws://localhost:8000/ws/feed?token=${token}`);

  socket.onopen = () => console.log("WebSocket connected");
  socket.onerror = (e) => console.error("WebSocket error:", e);
  socket.onclose = () => console.log("WebSocket disconnected");

  /**
   * Handles incoming WebSocket messages from the feed.
   * @param {MessageEvent} event - WebSocket message event containing a JSON payload.
   *
   * @description
   * Parses the message payload and applies the corresponding update to the UI.
   * Supported message types are:
   * - "new_post": add new post to the top of the list
   * - "new_comment" or "new_reaction": refresh the post with the given ID
   * - "delete_post": remove the post with the given ID from the list
   * All other message types are ignored.
   */
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    switch (message.type) {
      case "new_post":
        setPosts((prev) => [message.data, ...prev]);
        break;
      case "new_comment":
      case "new_reaction":
        refreshPostById(message.data.post_id);
        break;
      case "delete_post":
        setPosts((prev) => prev.filter((p) => p.id !== message.data.post_id));
        break;
      default:
        break;
    }
  };

  return socket;
}

// TODO: When scaling beyond feed updates, consider replacing this with a generic `createAppWebSocket` function.
// This new function should accept a `handlers` map (e.g., { new_post: fn, rsvp_update: fn, etc. }) and route
// incoming messages by type. Each page/component can then pass only the handlers it needs.
// This allows you to use a single WebSocket connection for the entire app and maintain clean separation of concerns.
