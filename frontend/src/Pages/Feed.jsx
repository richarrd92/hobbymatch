import { useEffect, useState } from "react";
import PostCard from "../components/PostCard";
import { fetchAllHobbies } from "../services/API/hobby";
import {createFeedWebSocket} from "../services/functions/websocket";
import "./Feed.css";

/**
 * Feed component displays the main posts feed for the user.
 * It fetches all hobbies, fetches posts, listens for real-time updates via WebSocket,
 * and supports refreshing individual posts upon reactions or comments.
 *
 * @param {Object} props
 * @param {Object} props.user - The current authenticated user object.
 * @param {string} props.token - Firebase ID token for authenticated API/WebSocket calls.
 *
 * @returns {JSX.Element} The feed page UI with posts, loading, and error handling.
 */
export default function Feed({ user, token }) {
  const [posts, setPosts] = useState(null);
  const [error, setError] = useState(null);

  const [hobbyMap, setHobbyMap] = useState({});

  useEffect(() => {
  /**
   * Loads all hobbies from backend and maps by ID, then sets the hobbyMap state.
   * Errors are logged to the console.
   */
    async function loadHobbies() {
      try {
        const allHobbies = await fetchAllHobbies();
        const map = {};
        for (const hobby of allHobbies) {
          map[hobby.id] = hobby.name;
        }
        setHobbyMap(map);
      } catch (err) {
        console.error("Failed to load hobbies:", err);
      }
    }

    loadHobbies();
  }, []);

  /**
   * Fetches posts feed data from backend API and updates state.
   * On error, sets the error state to display an error message.
   */
  async function fetchFeed() {
    try {
      const res = await fetch("http://localhost:8000/posts/feed");
      if (!res.ok) throw new Error("Failed to load feed");
      const data = await res.json();
      setPosts(data);
    } catch (err) {
      setError(err.message);
    }
  }

  // On mount: fetch initial feed and setup WebSocket for real-time post updates
  useEffect(() => {
    fetchFeed();
    const socket = createFeedWebSocket(token, { setPosts, refreshPostById });

    // Cleanup WebSocket connection on unmount
    return () => {
      socket.close();
    };
  }, []);

  /**
   * Fetches an updated post by ID from backend and replaces it in state.
   * Used to refresh individual post after reactions or comments.
   *
   * @param {number} postId - ID of the post to refresh.
   */
  async function refreshPostById(postId) {
    try {
      const res = await fetch(`http://localhost:8000/posts/${postId}`);
      if (!res.ok) throw new Error("Failed to fetch updated post");
      const updatedPost = await res.json();
      // Replace only the affected post
      setPosts((prevPosts) =>
        prevPosts.map((p) => (p.id === postId ? updatedPost : p))
      );
    } catch (err) {
      console.error("Failed to refresh post:", err);
    }
  }
  // Handle loading and error states
  if (error) {
    return (
      <main className="feed-container">
        <p className="error">Error: {error}</p>
      </main>
    );
  }

  // Handle loading state
  if (posts === null) {
    return (
      <main className="feed-container">
        <p>Loading posts...</p>
      </main>
    );
  }

  // Handle empty feed
  if (posts.length === 0) {
    return (
      <main className="feed-container">
        <p>No posts to display.</p>
      </main>
    );
  }

  // Render each post
  return (
    <main className="feed-container">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          currentUser={user}
          onReact={() => refreshPostById(post.id)}
          onComment={() => refreshPostById(post.id)}
          hobbyMap={hobbyMap}
        />
      ))}
    </main>
  );
}
