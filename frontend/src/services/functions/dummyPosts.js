// Initial array of dummy post objects for testing/display purposes
const dummyPosts = [
  {
    id: 1,
    user: "johndoe",
    avatar: "https://i.pravatar.cc/150?img=3", // User avatar image URL
    image: "https://images.unsplash.com/photo-1605296867304-46d5465a13f1", // Post image URL
    caption: "Loving the gym grind today!",
    hobby: "Fitness",
    timestamp: "2 hours ago",
  },
  {
    id: 2,
    user: "janesmith",
    avatar: "https://i.pravatar.cc/150?img=5",
    image: "https://images.unsplash.com/photo-1508780709619-79562169bc64",
    caption: "Nature heals 🌿",
    hobby: "Outdoors",
    timestamp: "5 hours ago",
  },
  {
    id: 3,
    user: "michaelc",
    avatar: "https://i.pravatar.cc/150?img=12",
    image: "https://images.unsplash.com/photo-1511376777868-611b54f68947",
    caption: "Late-night jam sessions hit different 🎸",
    hobby: "Music",
    timestamp: "8 hours ago",
  },
  {
    id: 4,
    user: "anika_p",
    avatar: "https://i.pravatar.cc/150?img=9",
    image: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620",
    caption: "Experimenting with watercolor techniques today!",
    hobby: "Art",
    timestamp: "1 day ago",
  },
  {
    id: 5,
    user: "kevinz",
    avatar: "https://i.pravatar.cc/150?img=15",
    image: "https://images.unsplash.com/photo-1518770660439-4636190af475",
    caption: "Hackathon vibes and coffee ☕️",
    hobby: "Technology",
    timestamp: "2 days ago",
  },
  {
    id: 6,
    user: "sara_o",
    avatar: "https://i.pravatar.cc/150?img=20",
    image: "https://images.unsplash.com/photo-1549576490-b0b4831ef60a",
    caption: "My first sourdough 🍞",
    hobby: "Cooking",
    timestamp: "3 days ago",
  },
];

// Duplicate posts with slight modifications to create a larger dummy data set
for (let i = 7; i <= 100; i++) {
  const base = dummyPosts[(i - 1) % 6]; // cycle through first 6 posts
  dummyPosts.push({
    ...base,
    id: i,
    caption: base.caption + (i % 2 === 0 ? " #hobbylife" : " #weekendVibes"), // add hashtags alternately
    timestamp: `${Math.floor(i / 2)} hours ago`, // increment time for variety
  });
}

export default dummyPosts;
