from .auth import LoginResponse, SignupRequest, LoginRequest
from .hobbies import HobbyCreate, HobbyRead, HobbyBase, HobbyUpdate, HobbyUpdateRequest, UserHobbyBase, UserHobbyRead
from .locations import LocationRead, LocationBase, LocationCreate, LocationResolveRequest
from .matches import MatchRead, MatchBase, MatchCreate
from .users import UserBase, UserCreate, UserRead, UserProfileUpdate

# Export all schemas
__all__ = [
    "LoginResponse",
    "SignupRequest",
    "LoginRequest",
    "HobbyCreate",
    "HobbyRead",
    "HobbyBase",
    "HobbyUpdate",
    "HobbyUpdateRequest",
    "LocationRead",
    "LocationBase",
    "LocationCreate",
    "LocationResolveRequest",
    "MatchRead",
    "MatchBase",
    "MatchCreate",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserProfileUpdate",
    "UserHobbyRead",
    "UserHobbyBase"
]