import PostCard from "../components/create/PostCard";
import "./Feed.css";

// Displays a list of posts or a message if none exist
export default function Feed({ posts }) {
  return (
    <main className="feed-container">
      {/* Show message if no posts */}
      {posts.length === 0 ? (
        <p>No posts to display.</p>
      ) : (
        // Map posts to PostCard components
        posts.map((post) => <PostCard key={post.id} post={post} />)
      )}
    </main>
  );
}
