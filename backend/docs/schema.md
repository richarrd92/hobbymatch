# Database Schema Overview

Users sign up via external providers like Google — no passwords stored. Each user selects up to **three hobbies**, ranked by interest (1 = most interested, 3 = least). These rankings power the matching algorithm connecting users based on shared or complementary interests.

**Match Types:**
- **Social:** General interest-based connections.
- **Mutual:** Both users share a top hobby and want to connect.
- **Trade:** One user wants to learn a hobby another user can teach.

Users communicate via threaded messages, leave reviews after meetings, and receive real-time notifications. Optional features include availability and location for more timely, relevant matches.

Users can:
- Post daily, short-lived content.
- Join hobby events with geolocations.
- RSVP to events; commitment history influences user reliability scores.

### Database Setup and Types

- Database: `hobbymatch_app`.
- Extension enabled: `uuid-ossp` for UUID generation.
- Enumerated types enforce data integrity:

| Enum Name         | Values                                  | Purpose                      |
|-------------------|-----------------------------------------|------------------------------|
| `hobby_rank`       | 1, 2, 3                                 | Hobby interest ranking        |
| `match_status`     | "pending", "accepted", "rejected", "completed" | Match lifecycle status       |
| `match_type`       | "social", "mutual", "trade"             | Match intent/type             |
| `event_status`     | "upcoming", "completed", "cancelled"    | Hobby event lifecycle         |
| `attendance_status`| "going", "not_going", "maybe", "flaked"| RSVP and attendance tracking  |

### Tables and Relationships

| Table Name        | Description                                                                                         |
|-------------------|-----------------------------------------------------------------------------------------------------|
| **Users**         | Stores user info (name, email, profile pic, bio, external auth data). Optional `location_id`.       |
| **User_Photos**   | Up to 3 additional user photos, with unique ordering per user.                                      |
| **Locations**      | Geographic data for cities, regions, and timezones.                                                |
| **Hobbies**        | Central hobby list with categories and optional tags.                                              |
| **User_Hobbies**   | Links users to ranked hobbies (1–3). Prevents duplicate user-hobby entries.                         |
| **Matches**        | Connects two users, tracking match status, type, and referenced hobbies.                           |
| **Messages**       | Chat messages within matches, supporting threaded replies.                                         |
| **Reviews**        | User feedback on matches, tied to specific hobbies.                                                |
| **Notifications**  | System alerts for matches, messages, reviews, etc.                                                 |
| **Availability**   | Optional user availability windows (days and times).                                              |
| **User_Posts**     | Temporary daily posts, expiring after 24 hours, optionally linked to hobbies.                       |
| **Hobby_Events**   | Events tagged with hobbies, supporting geo-location and status tracking.                           |
| **Event_Attendees**| Tracks RSVPs and attendance reliability, including flakes.                                        |
| **User_Flake_History** | Maintains reliability scores (1–10) for users based on attendance behavior.                    |

### Summary of Relationships

- **Users** are the central entity, linked to locations, hobbies, matches, messages, reviews, notifications, photos, and posts.
- **Hobbies** are shared interests; users select and rank them to drive matching.
- **Matches** represent social/trade connections referencing specific user hobbies.
- **Messages** enable communication inside matches.
- **Reviews** provide accountability post-interaction.
- **Notifications** keep users engaged with real-time updates.
- **Locations** support geographic features.
- **User_Photos** enhance profile personalization.
- **User_Posts** allow short-lived activity sharing.
- **Events and RSVPs** facilitate real-world meetups, supported by heatmap visualizations.
- **Flake history and reliability scores** encourage accountability and trustworthiness.

### Matching Logic Flow

#### 1. Initial Matching: Hobby Overlap

- **Exact Match (Strongest):** Users share the same top 3 hobbies in the exact order.
  
  *Example:*  
  User A: 1. Soccer, 2. Movies, 3. Music  
  User B: 1. Soccer, 2. Movies, 3. Music  
  → Perfect match

- **Partial Match (Medium to Strong):** Some shared hobbies with rank differences.
  
  *Example:*  
  User A: 1. Soccer, 2. Music, 3. Movies  
  User B: 1. Movies, 2. Soccer, 3. Gaming  
  → Moderate match

- **Low Match (Weaker):** Share only 1 hobby or similar categories.

#### 2. Ranking Weight (1–3 scale)

| Rank Pair | Match Score Impact      |
|-----------|------------------------|
| 3 & 3     | +3 (Very strong)       |
| 2 & 2     | +2 (Strong)            |
| 1 & 1     | +1 (Moderate)          |
| 3 & 2     | +1.5 (Good)            |
| 1 & 3     | +0.5 (Weak)            |

#### 3. Category Boost

- Even if hobbies differ, shared categories (e.g., outdoors) add compatibility.

#### 4. Future Boosters (Optional)

- **Location:** Users in the same city or region get a higher match score.
- **Age Range:** Users can set preferred age ranges.
- **User Posts:** Recent hobby-tagged posts improve recommendation relevance.
- **User Photos:** Visual appeal can enhance match engagement.
- **Availability:** Overlapping availability can improve meeting feasibility.

#### 5. Match Type and Intent

- **Social:** General interest connections.
- **Mutual:** Shared skill/hobby connections.
- **Trade:** Skill-teaching relationships.

### Summary

The HobbyMatch schema and logic support a dynamic, scalable social platform connecting users through hobbies, events, and community interactions. It is designed to encourage real-world connections, accountability, and rich user experiences with room to grow future features like location-based matching and intelligent content recommendations.