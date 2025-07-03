from pydantic import BaseModel
from uuid import UUID

# Request schema for login
class LoginRequest(BaseModel):
    id_token: str

# Request schema for signup
class SignupRequest(BaseModel):
    id_token: str

# Response schema for login/signup
class LoginResponse(BaseModel):
    token: str
    role: str
    id: UUID
    name: str
    email: str

# TODO Notes for future implementation:
# - Add support for traditional email/password login
# - Add fields for additional signup methods (e.g., GitHub, Apple)
# - Include refresh token or multi-factor auth status in response