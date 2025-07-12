import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./PostCard.css";
import { reactToPost, addComment } from "../services/API/posts";
import formatTimestamp from "../services/functions/formatTimestamp";

/** @type {Object.<string, string>} Mapping of reaction types to emojis */
const reactionEmojis = {
  like: "👍",
  love: "❤️",
  fire: "🔥",
  laugh: "😂",
  sad: "😢",
};

/**
 * PostCard component displays a single post with content, reactions, comments, and user profile info.
 *
 * @param {Object} props
 * @param {Object} props.post - The post data
 * @param {Object} props.currentUser - The currently logged-in user
 * @param {Function} [props.onReact] - Optional callback to refresh parent state on reaction
 * @param {Function} [props.onComment] - Optional callback to refresh parent state on comment
 * @param {Object} props.hobbyMap - Mapping of hobby_id to hobby name
 */
export default function PostCard({
  post,
  currentUser,
  onReact,
  onComment,
  hobbyMap,
}) {
  const navigate = useNavigate();
  const [commentsVisible, setCommentsVisible] = useState(false);
  const [newComment, setNewComment] = useState("");

  // Navigate to the post author's profile page.
  const handleProfileClick = () => navigate(`/profile/${post.user_id}`);

  /** @type {string} Resolved hobby name or fallback */
  const hobbyName = post.hobby_id
    ? hobbyMap[post.hobby_id] || "Unknown"
    : "General";

  /**
   * Sends a reaction to the backend and triggers post refresh if provided.
   * @param {string} type - Reaction type (like, love, etc.)
   */
  const handleReaction = async (type) => {
    try {
      await reactToPost(post.id, type);

      // Refresh post on react
      if (onReact) onReact();
    } catch (err) {
      console.error(err.message);
    }
  };

  /**
   * Submits a new comment to the backend and clears input.
   * Refreshes post if callback provided.
   * @param {React.FormEvent} e
   */
  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await addComment(post.id, newComment);
      setNewComment("");
      // Refresh post on comment
      if (onComment) onComment();
    } catch (err) {
      console.error(err.message);
    }
  };

  return (
    <div className="post-card">
      {/* Header */}
      <div className="post-header">
        <img
          src={
            post.profile_pic_url ||
            `https://i.pravatar.cc/150?u=${post.user_id}`
          }
          alt={`${post.name}'s avatar`}
          className="avatar"
          onClick={handleProfileClick}
        />
        {/* User info */}
        <div className="user-info">
          <button className="username" onClick={handleProfileClick}>
            {post.name}
          </button>
          <span className="post-meta">
            {hobbyName} · {formatTimestamp(post.created_at)}
          </span>
        </div>
      </div>
      {/* Image */}
      {post.image_url && (
        <img src={post.image_url} alt="Post" className="post-image" />
      )}
      {/* Reactions */}
      <div className="reactions">
        {Object.entries(reactionEmojis).map(([type, emoji]) => (
          <button
            key={type}
            className="reaction-btn"
            onClick={() => handleReaction(type)}
          >
            {emoji} {post.reaction_counts?.[type] || 0}
          </button>
        ))}
      </div>
      {/* Post content */}
      <div className="post-body">
        <p className="caption">
          <strong>
            <button className="inline-username" onClick={handleProfileClick}>
              {post.name}
            </button>
          </strong>{" "}
          {post.content}
        </p>
      </div>

      {/* Comments section */}
      <div className="comments-section">
        {/* Toggle comments */}
        {post.comments?.length > 0 && (
          <button
            className="view-comments-toggle"
            onClick={() => setCommentsVisible(!commentsVisible)}
          >
            {commentsVisible
              ? "Hide comments"
              : `View comments${
                  post.comments?.length ? ` (${post.comments.length})` : ""
                }`}
          </button>
        )}

        {/* Comment list */}
        {commentsVisible &&
          post.comments?.map((comment) => (
            <div key={comment.id} className="comment">
              <strong>{comment.user_name}</strong> {comment.content}
            </div>
          ))}

        {/* Add new comment */}
        {currentUser && (
          <form onSubmit={handleCommentSubmit} className="comment-form">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
            />
            {/* Add a submit button */}
            <button type="submit" disabled={!newComment.trim()}>
              Post
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
