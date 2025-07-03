import enum

# Status of a match between users
class MatchStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"

# Type of match interaction
class MatchType(str, enum.Enum):
    social = "social"
    trade = "trade"
    mutual = "mutual"

# User roles in the system
class UserRole(str, enum.Enum):
    user = "user"
    moderator = "moderator" # TODO: Reserved for moderation features
    admin = "admin"

# Types of in-app notifications
class NotificationType(str, enum.Enum):
    match_request = "match_request"
    message = "message"
    review = "review"
    system = "system"

# Categories of hobbies
class HobbyCategory(str, enum.Enum):
    sports = "sports"
    entertainment = "entertainment"
    education = "education"
    games = "games"
    arts = "arts"
    technology = "technology"
    outdoors = "outdoors"
    other = "other"

# Types of reactions users can give
class ReactionType(str, enum.Enum):
    like = "like"
    love = "love"
    fire = "fire"
    laugh = "laugh"
    sad = "sad"

# RSVP status for events
class RsvpStatus(str, enum.Enum):
    going = "going"
    interested = "interested"
    not_going = "not_going"
    flaked = "flaked"
    attended = "attended"

# Event format type
class EventType(str, enum.Enum):
    virtual = "virtual"
    in_person = "in-person"