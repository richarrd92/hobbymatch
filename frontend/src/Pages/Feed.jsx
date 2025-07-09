import { useEffect, useState } from "react";
import PostCard from "../components/PostCard";
import { fetchAllHobbies } from "../services/API/hobby";
import "./Feed.css";

// Feed Page
export default function Feed({ user }) {
  const [posts, setPosts] = useState(null);
  const [error, setError] = useState(null);

  const [hobbyMap, setHobbyMap] = useState({});

  // Load all hobbies once and map by ID
  useEffect(() => {
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

  // Fetch posts from the backend
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

  // Fetch on mount + refresh every 10s
  useEffect(() => {
    fetchFeed(); // fetch once on mount
    const interval = setInterval(() => {
      fetchFeed(); // refresh every 10 seconds
    }, 10000);
    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  // Refresh only affected post
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
