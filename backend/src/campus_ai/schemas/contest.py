"""
赛事模块 Schema
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from campus_ai.models.contest import (
    ContestLevel, ContestStatus, TeamStatus,
    TeamMemberRole, ApplicationStatus
)


# ============== 赛事相关 ==============

class ContestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="赛事标题")
    summary: Optional[str] = Field(None, max_length=500, description="赛事摘要")
    description: Optional[str] = Field(None, description="详细描述")
    level: ContestLevel = Field(ContestLevel.SCHOOL, description="赛事级别")
    category: str = Field(..., max_length=50, description="赛事分类")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    registration_start: Optional[datetime] = Field(None, description="报名开始时间")
    registration_end: Optional[datetime] = Field(None, description="报名截止时间")
    contest_start: Optional[datetime] = Field(None, description="比赛开始时间")
    contest_end: Optional[datetime] = Field(None, description="比赛结束时间")
    organizer: Optional[str] = Field(None, max_length=255, description="主办方")
    contact: Optional[str] = Field(None, max_length=255, description="联系方式")
    brief_description: Optional[str] = Field(None, description="简洁说明")
    eligibility_requirements: Optional[str] = Field(None, description="参赛资格")
    participation_process: Optional[str] = Field(None, description="参赛流程")
    awards_info: Optional[str] = Field(None, description="奖项信息")
    contact_info: Optional[str] = Field(None, description="联系方式详情")
    recommendations: Optional[str] = Field(None, description="推荐建议")


class ContestCreate(ContestBase):
    source: str = Field("manual", description="来源")
    source_url: Optional[str] = Field(None, max_length=500, description="来源URL")


class ContestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    level: Optional[ContestLevel] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    contest_start: Optional[datetime] = None
    contest_end: Optional[datetime] = None
    status: Optional[ContestStatus] = None
    organizer: Optional[str] = Field(None, max_length=255)
    contact: Optional[str] = Field(None, max_length=255)


class ContestResponse(ContestBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: ContestStatus
    source: str
    source_url: Optional[str] = None
    is_ai_processed: bool
    needs_review: bool
    view_count: int
    team_count: int
    created_at: datetime
    updated_at: datetime


class ContestListResponse(BaseModel):
    total: int
    items: List[ContestResponse]


# ============== 队伍相关 ==============

class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="队伍名称")
    description: Optional[str] = Field(None, description="队伍描述")
    max_members: int = Field(5, ge=2, le=20, description="最大人数")
    required_skills: Optional[List[str]] = Field(default_factory=list, description="需要的技能")
    preferred_major: Optional[str] = Field(None, max_length=255, description="偏好专业")


class TeamCreate(TeamBase):
    contest_id: str = Field(..., description="赛事ID")


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    max_members: Optional[int] = Field(None, ge=2, le=20)
    required_skills: Optional[List[str]] = None
    preferred_major: Optional[str] = Field(None, max_length=255)
    status: Optional[TeamStatus] = None


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    role: TeamMemberRole
    skills: Optional[List[str]] = None
    joined_at: datetime


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contest_id: str
    status: TeamStatus
    members: List[TeamMemberResponse]
    created_at: datetime
    updated_at: datetime


class TeamListResponse(BaseModel):
    total: int
    items: List[TeamResponse]


# ============== 组队申请相关 ==============

class TeamApplicationCreate(BaseModel):
    team_id: str = Field(..., description="队伍ID")
    message: Optional[str] = Field(None, description="申请留言")


class TeamApplicationHandle(BaseModel):
    approved: bool = Field(..., description="是否通过")
    handled_message: Optional[str] = Field(None, description="处理留言")


class TeamApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    applicant_id: str
    message: Optional[str] = None
    status: ApplicationStatus
    handled_at: Optional[datetime] = None
    handled_message: Optional[str] = None
    created_at: datetime


# ============== 任务相关 ==============

class TeamTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    assigned_to: Optional[str] = Field(None, description="分配给")
    due_date: Optional[datetime] = Field(None, description="截止日期")


class TeamTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


# ============== 用户标签相关 ==============

class UserContestTagCreate(BaseModel):
    tag: str = Field(..., min_length=1, max_length=50, description="标签")
    weight: int = Field(1, ge=1, description="权重")


# ============== 爬虫相关 ==============

class CrawlRequest(BaseModel):
    url: Optional[str] = Field(None, description="目标URL，不填则使用默认列表页")
    max_pages: int = Field(5, ge=1, le=50, description="最大爬取页数")


# ============== 推荐相关 ==============

class ContestRecommendRequest(BaseModel):
    user_skills: Optional[List[str]] = Field(default_factory=list, description="用户技能")
    limit: int = Field(10, ge=1, le=50, description="推荐数量")


# ============== 评论相关 ==============

class ContestCommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[str] = Field(None, description="父评论ID（回复时使用）")


class ContestCommentCreate(ContestCommentBase):
    contest_id: str = Field(..., description="赛事ID")


class ContestCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)


class ContestCommentResponse(ContestCommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contest_id: str
    user_id: str
    like_count: int
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class ContestCommentListResponse(BaseModel):
    total: int
    items: List[ContestCommentResponse]


# ============== 私信相关 ==============

class PrivateMessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")
    receiver_id: str = Field(..., description="接收者ID")


class PrivateMessageCreate(PrivateMessageBase):
    pass


class PrivateMessageResponse(PrivateMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sender_id: str
    is_read: bool
    created_at: datetime


class PrivateMessageListResponse(BaseModel):
    total: int
    items: List[PrivateMessageResponse]


class PrivateConversationResponse(BaseModel):
    user_id: str
    last_message: Optional[PrivateMessageResponse] = None
    unread_count: int
