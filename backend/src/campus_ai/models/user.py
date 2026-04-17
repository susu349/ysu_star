from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, comment="用户ID（学号/工号）")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=True, index=True, comment="邮箱")
    phone = Column(String(20), unique=True, nullable=True, index=True, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    role = Column(String(20), nullable=False, default="student", comment="角色：student/teacher/admin")
    department = Column(String(100), nullable=True, comment="院系")
    major = Column(String(100), nullable=True, comment="专业")
    grade = Column(String(20), nullable=True, comment="年级")
    tags = Column(JSON, nullable=True, default=list, comment="个人标签（技能、兴趣等）")
    bio = Column(Text, nullable=True, comment="个人简介")
    privacy_settings = Column(JSON, nullable=True, default=dict, comment="隐私设置")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否已实名认证")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
