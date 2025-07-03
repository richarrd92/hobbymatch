import "./PostCard.css";

export default function PostCard({ post }) {
  return (
    <div className="post-card">
      {/* Top section: user avatar and info */}
      <div className="post-header">
        <img src={post.avatar} alt="avatar" className="avatar" />
        <div className="user-info">
          <span className="username">{post.user}</span>
          <span className="post-meta">
            {post.hobby} · {post.timestamp}
          </span>
        </div>
      </div>

      {/* Main post image */}
      <img src={post.image} alt="post" className="post-image" />

      {/* Post caption */}
      <div className="post-body">
        <p className="caption">
          <strong>@{post.user}</strong> {post.caption}
        </p>
      </div>
    </div>
  );
}
