-- Create the database
CREATE DATABASE hobbymatch_app;

---------------- WARNING: This will delete all data! ----------------
-- Reset the database for testing: 
-- Drop all tables and enums in dependency-safe order
DROP TABLE IF EXISTS 
    spot_rsvps,
    live_hobby_spots,
    event_rsvps,
    events,
    post_comments,
    post_reactions,
    user_posts,
    user_flake_scores,
    user_connections,
    user_points,
    user_streaks,
    notifications,
    reviews,
    messages,
    matches,
    user_hobbies,
    hobbies,
    users,
    locations 
CASCADE;

DROP TYPE IF EXISTS 
    rsvp_status,
    event_type,
    reaction_type,
    notification_type,
    user_role,
    match_type,
    match_status,
    hobby_category 
CASCADE;

-- Enable UUID extension to support uuid_generate_v4()
-- This is used for auto-generating globally unique primary keys in tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ENUM TYPES
CREATE TYPE match_status AS ENUM ('pending', 'accepted', 'rejected', 'completed'); -- Lifecycle states of user matches
CREATE TYPE match_type AS ENUM ('social', 'trade', 'mutual'); -- Match type: social = shared interest, trade = skill exchange, mutual = equal skillset
CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin'); -- User role for access control and permissions
CREATE TYPE notification_type AS ENUM ('match_request', 'message', 'review', 'system'); -- Types of notifications sent to users
CREATE TYPE hobby_category AS ENUM (
  'Sports',
  'Outdoors',
  'Creative',
  'Music',
  'Culinary',
  'Crafts',
  'Tech',
  'Games',
  'Lifestyle',
  'Wellness',
  'Fitness',
  'Entertainment',
  'Nature',
  'Finance',
  'Community',
  'Academic'
);

CREATE TYPE reaction_type AS ENUM ('like', 'love', 'fire', 'laugh', 'sad'); -- Types of reactions users can give to posts
CREATE TYPE rsvp_status AS ENUM ('going', 'interested', 'not_going', 'flaked', 'attended'); -- RSVP status for events and live spots
CREATE TYPE event_type AS ENUM ('virtual', 'in-person'); -- Event type for meetups

-- Table: locations
-- Stores geographic info (city, region, country, coordinates, timezone)
-- Used for proximity matching, event locations, and heatmap spots
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique location identifier
    city VARCHAR(100), -- City name (e.g., Baltimore)
    region VARCHAR(100), -- State or province (e.g., MD)
    country VARCHAR(100), -- Country name (e.g., USA)
    latitude DECIMAL(9,6), -- Latitude coordinate for mapping
    longitude DECIMAL(9,6), -- Longitude coordinate for mapping
    timezone VARCHAR(100) -- Timezone string for scheduling
);

-- Table: users
-- Stores user profiles, authentication info, and preferences
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique user identifier
    firebase_uid VARCHAR(128) UNIQUE NOT NULL, -- Firebase UID
    name VARCHAR(100) NOT NULL, -- Display name
    email VARCHAR(255) UNIQUE NOT NULL, -- Unique login email
    age INTEGER CHECK (age > 0), -- Optional age for filtering & verification
    bio TEXT, -- User biography or introduction
    profile_pic_url TEXT, -- URL for profile image/avatar
    location_id UUID, -- FK to locations table (nullable)
    role user_role DEFAULT 'user', -- Role for access control
    is_verified BOOLEAN DEFAULT FALSE, -- Verified user flag (premium/ID verified)
    verification_method VARCHAR(50), -- Method used for verification ('photo', 'id', etc.)
    is_private BOOLEAN DEFAULT FALSE, -- If TRUE, hides user from public matching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Account creation timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Profile last update timestamp
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- Table: hobbies
-- Central list of all hobby/skill options users can select
CREATE TABLE hobbies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category hobby_category NOT NULL,
    created_by UUID, -- Should be an admin (enforced in app logic)
    is_active BOOLEAN DEFAULT TRUE, -- Can deactivate without deleting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Table: user_hobbies
-- Links users to their hobbies with rank for matching priority
CREATE TABLE user_hobbies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    hobby_id UUID NOT NULL,
    rank INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 3), -- Must be 1, 2, or 3
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(id) ON DELETE CASCADE,
    UNIQUE(user_id, hobby_id),
    UNIQUE(user_id, rank) -- Prevent duplicate ranks (i.e., only one rank 1, 2, 3)
);


-- Table: matches
-- Stores match requests and accepted matches between users based on hobbies
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique match ID
    initiator_id UUID NOT NULL, -- User who initiated match
    receiver_id UUID NOT NULL, -- User invited to match
    initiator_hobby_id UUID, -- FK to initiator’s hobby in user_hobbies (nullable)
    receiver_hobby_id UUID, -- FK to receiver’s hobby in user_hobbies (nullable)
    match_type match_type DEFAULT 'social', -- Match category
    status match_status DEFAULT 'pending', -- Current match status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (initiator_hobby_id) REFERENCES user_hobbies(id) ON DELETE SET NULL,
    FOREIGN KEY (receiver_hobby_id) REFERENCES user_hobbies(id) ON DELETE SET NULL
);

-- Table: messages
-- Stores chat messages between matched users, supports threaded replies
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique message ID
    match_id UUID NOT NULL, -- FK to related match conversation
    sender_id UUID NOT NULL, -- User who sent the message
    content TEXT NOT NULL, -- Message body text
    reply_to_message_id UUID, -- FK to message being replied to (nullable)
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to_message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Table: reviews
-- User feedback on completed matches
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique review ID
    match_id UUID NOT NULL, -- FK to match reviewed
    reviewer_id UUID NOT NULL, -- User who wrote review
    reviewee_id UUID NOT NULL, -- User being reviewed
    hobby_id UUID NOT NULL, -- Hobby focused on in match
    rating INTEGER CHECK (rating BETWEEN 1 AND 5), -- Rating score 1-5
    comment TEXT, -- Optional review text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(id) ON DELETE CASCADE
);

-- Table: notifications
-- Alerts sent to users for various events
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique notification ID
    user_id UUID NOT NULL, -- Recipient user
    type notification_type NOT NULL, -- Type of notification
    reference_id UUID, -- Related object (match, message, review)
    content TEXT, -- Notification message content
    is_read BOOLEAN DEFAULT FALSE, -- Read/unread status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: user_posts
-- User-created ephemeral posts tied to hobbies and expiring after 24 hours
CREATE TABLE user_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique post ID
    user_id UUID NOT NULL, -- Authoring user
    content TEXT NOT NULL, -- Post content (text, media links)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    expires_at TIMESTAMP NOT NULL, -- Expiration time (usually created_at + 24h)
    hobby_id UUID, -- Related hobby (optional)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(id) ON DELETE SET NULL
);

-- Table: post_reactions
-- Emoji reactions (like, love, fire, etc.) on user posts
CREATE TABLE post_reactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique reaction ID
    post_id UUID NOT NULL, -- FK to reacted post
    user_id UUID NOT NULL, -- Reacting user
    type reaction_type NOT NULL, -- Reaction type/emoji
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES user_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(post_id, user_id, type) -- Prevent duplicate reactions by same user on same post
);

-- Table: post_comments
-- Comments on user posts for lightweight interaction
CREATE TABLE post_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique comment ID
    post_id UUID NOT NULL, -- FK to commented post
    user_id UUID NOT NULL, -- Comment author
    content TEXT NOT NULL, -- Comment text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES user_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: user_streaks
-- Tracks user posting/activity streaks for rewards and motivation
CREATE TABLE user_streaks (
    user_id UUID PRIMARY KEY, -- FK to user
    current_streak INTEGER DEFAULT 0, -- Current consecutive active days
    longest_streak INTEGER DEFAULT 0, -- User’s best streak record
    last_active DATE, -- Date of last recorded activity
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: user_points
-- Engagement or reputation points for gamification
CREATE TABLE user_points (
    user_id UUID PRIMARY KEY, -- FK to user
    points INTEGER DEFAULT 0, -- Points total
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: events
-- User-created hobby-related events (in-person or virtual)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique event ID
    host_id UUID NOT NULL, -- Event creator
    title VARCHAR(100), -- Event title
    description TEXT, -- Event details
    event_type event_type NOT NULL, -- 'virtual' or 'in-person'
    location_id UUID, -- Location for in-person events
    start_time TIMESTAMP, -- Event start time
    end_time TIMESTAMP, -- Event end time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- Table: event_rsvps
-- RSVP records for events, tracking user interest and attendance
CREATE TABLE event_rsvps (
    event_id UUID NOT NULL, -- FK to event
    user_id UUID NOT NULL, -- Attending/interested user
    status rsvp_status DEFAULT 'going', -- RSVP status
    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flake_score_at_rsvp INTEGER, -- Snapshot of user's flake score at RSVP time
    PRIMARY KEY (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: live_hobby_spots
-- User-created geolocated spots for spontaneous hobby meetups
CREATE TABLE live_hobby_spots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique spot ID
    created_by UUID NOT NULL, -- User who created the spot
    hobby_id UUID NOT NULL, -- Hobby associated with spot
    title VARCHAR(100), -- Spot title (e.g., "Pickup Soccer @ Riverside")
    description TEXT, -- Optional details
    latitude DECIMAL(9,6) NOT NULL, -- Spot latitude
    longitude DECIMAL(9,6) NOT NULL, -- Spot longitude
    start_time TIMESTAMP NOT NULL, -- Meetup start time
    end_time TIMESTAMP, -- Optional end time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(id) ON DELETE CASCADE
);

-- Table: spot_rsvps
-- Tracks user RSVPs to live hobby spots, used for heatmap intensity & flake tracking
CREATE TABLE spot_rsvps (
    spot_id UUID NOT NULL, -- FK to live hobby spot
    user_id UUID NOT NULL, -- Attending user
    status rsvp_status DEFAULT 'going', -- RSVP status (going, flaked, attended, etc.)
    rsvp_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flake_score_at_rsvp INTEGER, -- Snapshot of flake score at RSVP time
    PRIMARY KEY (spot_id, user_id),
    FOREIGN KEY (spot_id) REFERENCES live_hobby_spots(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: user_flake_scores
-- Tracks reliability of user attendance (1=very flaky to 10=very reliable)
CREATE TABLE user_flake_scores (
    user_id UUID PRIMARY KEY, -- FK to user
    total_rsvps INTEGER DEFAULT 0, -- Total RSVP count
    attended INTEGER DEFAULT 0, -- Attended count
    flaked INTEGER DEFAULT 0, -- Missed RSVP count
    flake_score INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN total_rsvps = 0 THEN 10
            ELSE GREATEST(1, 10 - ROUND((flaked::DECIMAL / total_rsvps) * 10))
        END
    ) STORED, -- Computed score (10 = perfect reliability)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: user_connections
-- Stores friend/follow relationships and interaction history
CREATE TABLE user_connections (
    user_id UUID NOT NULL, -- Owner user
    connected_user_id UUID NOT NULL, -- Connected/friend user
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When connection formed
    PRIMARY KEY (user_id, connected_user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (connected_user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- TODO: Future additions
-- - Add user_photos table to store 1–3 photos per profile
-- - Add reporting, blocking, or user activity history if needed
-- - Consider audit tables for sensitive operations