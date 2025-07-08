import "./Feed.css";

// Displays a list of posts or a message if none exist
export default function Feed({ posts }) {
  return (
    <main className="feed-container">
      {posts.length === 0 ? (
        <p>No posts to display.</p>
      ) : (
        posts.map((post) => (
          <div className="post-card" key={post.id}>
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
        ))
      )}
    </main>
  );
}
