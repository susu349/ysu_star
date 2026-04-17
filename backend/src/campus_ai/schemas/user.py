from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")


class UserCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50, description="学号/工号")
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str = Field(default="student", description="角色")


class UserLogin(BaseModel):
    id: str = Field(..., description="学号/工号")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class TokenRefresh(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    tags: Optional[List[str]] = None
    bio: Optional[str] = None
    privacy_settings: Optional[Dict[str, Any]] = None


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    avatar: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    tags: Optional[List[str]] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    department: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    tags: Optional[List[str]] = None
    bio: Optional[str] = None
    created_at: datetime
