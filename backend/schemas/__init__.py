from .auth import LoginResponse, SignupRequest, LoginRequest
from .hobbies import HobbyCreate, HobbyRead, HobbyBase
from .locations import LocationRead, LocationBase, LocationCreate, LocationResolveRequest
from .matches import MatchRead, MatchBase, MatchCreate
from .user_hobbies import UserHobbyCreate, UserHobbyRead, UserHobbyBase
from .users import UserBase, UserCreate, UserRead, UserProfileUpdate

# Export all schemas
__all__ = [
    "LoginResponse",
    "SignupRequest",
    "LoginRequest",
    "HobbyCreate",
    "HobbyRead",
    "HobbyBase",
    "LocationRead",
    "LocationBase",
    "LocationCreate",
    "LocationResolveRequest",
    "MatchRead",
    "MatchBase",
    "MatchCreate",
    "UserHobbyCreate",
    "UserHobbyRead",
    "UserHobbyBase",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserProfileUpdate"
]