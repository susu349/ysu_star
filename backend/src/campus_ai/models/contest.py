"""
赛事模块相关数据模型
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class ContestLevel(str, enum.Enum):
    """赛事级别"""
    SCHOOL = "school"         # 校赛
    PROVINCE = "province"     # 省赛
    NATIONAL = "national"     # 国赛
    INTERNATIONAL = "international"  # 国际赛


class ContestStatus(str, enum.Enum):
    """赛事状态"""
    DRAFT = "draft"               # 草稿
    PENDING = "pending"           # 待审核
    PUBLISHED = "published"       # 已发布
    REGISTRATION_OPEN = "registration_open"    # 报名中
    REGISTRATION_CLOSED = "registration_closed" # 报名截止
    ONGOING = "ongoing"           # 进行中
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消


class TeamStatus(str, enum.Enum):
    """队伍状态"""
    RECRUITING = "recruiting"     # 招募中
    FULL = "full"                 # 已满员
    CLOSED = "closed"             # 已关闭
    DISBANDED = "disbanded"       # 已解散


class TeamMemberRole(str, enum.Enum):
    """队伍成员角色"""
    LEADER = "leader"             # 队长
    MEMBER = "member"             # 队员
    VICE_LEADER = "vice_leader"   # 副队长


class ApplicationStatus(str, enum.Enum):
    """组队申请状态"""
    PENDING = "pending"           # 待审核
    APPROVED = "approved"         # 已通过
    REJECTED = "rejected"         # 已拒绝
    WITHDRAWN = "withdrawn"       # 已撤回


class Contest(Base):
    """赛事主表"""
    __tablename__ = "contests"

    id = Column(String(50), primary_key=True, comment="赛事ID")
    title = Column(String(255), nullable=False, index=True, comment="赛事标题")
    summary = Column(String(500), nullable=True, comment="100字以内极简摘要")
    description = Column(Text, nullable=True, comment="详细描述")

    # AI生成的增强信息
    brief_description = Column(Text, nullable=True, comment="简洁说明：200-300字，适合卡片展示")
    participation_process = Column(Text, nullable=True, comment="参赛流程：分步骤说明")
    contact_info = Column(Text, nullable=True, comment="联系方式：联系人、电话、邮箱、QQ等")
    recommendations = Column(Text, nullable=True, comment="推荐建议：适合人群、备赛建议、注意事项")
    eligibility_requirements = Column(Text, nullable=True, comment="参赛资格：专业、年级、人数限制等")
    awards_info = Column(Text, nullable=True, comment="奖项信息：奖项设置、奖品、学分认定等")

    # 赛事分类
    level = Column(String(20), nullable=False, index=True, comment="赛事级别")
    category = Column(String(50), nullable=False, index=True, comment="赛事分类：学科/科技/文体等")
    tags = Column(JSON, nullable=True, default=list, comment="标签列表")

    # 时间信息
    registration_start = Column(DateTime(timezone=True), nullable=True, comment="报名开始时间")
    registration_end = Column(DateTime(timezone=True), nullable=True, comment="报名截止时间")
    contest_start = Column(DateTime(timezone=True), nullable=True, comment="比赛开始时间")
    contest_end = Column(DateTime(timezone=True), nullable=True, comment="比赛结束时间")

    # 来源信息
    source = Column(String(20), nullable=False, default="crawler", comment="来源：manual/crawler/user")
    source_url = Column(String(500), nullable=True, comment="来源URL")
    source_file = Column(String(255), nullable=True, comment="附件路径")

    # 原始数据（用于AI处理）
    raw_content = Column(Text, nullable=True, comment="原始爬取内容")
    raw_html = Column(Text, nullable=True, comment="原始HTML")

    # 状态
    status = Column(String(20), nullable=False, default="draft", comment="赛事状态")
    is_ai_processed = Column(Boolean, default=False, nullable=False, comment="是否已AI处理")
    needs_review = Column(Boolean, default=False, nullable=False, comment="是否需要人工复核")

    # 主办方信息
    organizer = Column(String(255), nullable=True, comment="主办方")
    contact = Column(String(255), nullable=True, comment="联系方式")

    # 统计
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")
    team_count = Column(Integer, default=0, nullable=False, comment="组队数量")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    teams = relationship("Team", back_populates="contest", cascade="all, delete-orphan")
    attachments = relationship("ContestAttachment", back_populates="contest", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Contest(id={self.id}, title={self.title}, level={self.level})>"


class Team(Base):
    """队伍表"""
    __tablename__ = "teams"

    id = Column(String(50), primary_key=True, comment="队伍ID")
    contest_id = Column(String(50), ForeignKey("contests.id"), nullable=False, index=True, comment="赛事ID")
    name = Column(String(100), nullable=False, comment="队伍名称")
    description = Column(Text, nullable=True, comment="队伍描述")

    # 招募要求
    max_members = Column(Integer, default=5, nullable=False, comment="最大人数")
    required_skills = Column(JSON, nullable=True, default=list, comment="需要的技能标签")
    preferred_major = Column(String(255), nullable=True, comment="偏好专业")

    # 状态
    status = Column(String(20), nullable=False, default="recruiting", comment="队伍状态")

    # 任务管理
    tasks = Column(JSON, nullable=True, default=list, comment="任务列表")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    contest = relationship("Contest", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    applications = relationship("TeamApplication", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name={self.name}, contest_id={self.contest_id})>"


class TeamMember(Base):
    """队伍成员表"""
    __tablename__ = "team_members"

    id = Column(String(50), primary_key=True, comment="成员ID")
    team_id = Column(String(50), ForeignKey("teams.id"), nullable=False, index=True, comment="队伍ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    role = Column(String(20), nullable=False, default="member", comment="角色")
    skills = Column(JSON, nullable=True, default=list, comment="技能标签")
    assigned_tasks = Column(JSON, nullable=True, default=list, comment="分配的任务")

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="加入时间")

    # 关系
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<TeamMember(id={self.id}, team_id={self.team_id}, user_id={self.user_id})>"


class TeamApplication(Base):
    """组队申请表"""
    __tablename__ = "team_applications"

    id = Column(String(50), primary_key=True, comment="申请ID")
    team_id = Column(String(50), ForeignKey("teams.id"), nullable=False, index=True, comment="队伍ID")
    applicant_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="申请人ID")

    message = Column(Text, nullable=True, comment="申请留言")
    status = Column(String(20), nullable=False, default="pending", comment="状态")

    handled_by = Column(String(50), ForeignKey("users.id"), nullable=True, comment="处理人ID")
    handled_at = Column(DateTime(timezone=True), nullable=True, comment="处理时间")
    handled_message = Column(Text, nullable=True, comment="处理留言")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    team = relationship("Team", back_populates="applications")
    applicant = relationship("User", foreign_keys=[applicant_id])
    handler = relationship("User", foreign_keys=[handled_by])

    def __repr__(self) -> str:
        return f"<TeamApplication(id={self.id}, team_id={self.team_id}, status={self.status})>"


class ContestMilestone(Base):
    """赛事里程碑提醒表"""
    __tablename__ = "contest_milestones"

    id = Column(String(50), primary_key=True, comment="里程碑ID")
    contest_id = Column(String(50), ForeignKey("contests.id"), nullable=False, index=True, comment="赛事ID")
    title = Column(String(255), nullable=False, comment="里程碑标题")
    description = Column(Text, nullable=True, comment="描述")
    milestone_date = Column(DateTime(timezone=True), nullable=False, comment="里程碑日期")
    reminder_type = Column(String(20), nullable=False, default="once", comment="提醒类型：once/recurring")
    is_sent = Column(Boolean, default=False, nullable=False, comment="是否已发送提醒")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    def __repr__(self) -> str:
        return f"<ContestMilestone(id={self.id}, contest_id={self.contest_id}, title={self.title})>"


class ContestAttachment(Base):
    """赛事附件表"""
    __tablename__ = "contest_attachments"

    id = Column(String(50), primary_key=True, comment="附件ID")
    contest_id = Column(String(50), ForeignKey("contests.id"), nullable=False, index=True, comment="赛事ID")

    name = Column(String(255), nullable=False, comment="附件名称")
    url = Column(String(500), nullable=False, comment="原始URL")
    file_path = Column(String(500), nullable=True, comment="本地存储路径")
    file_type = Column(String(50), nullable=True, comment="文件类型：pdf/doc/docx/xls/xlsx/zip等")
    file_size = Column(Integer, nullable=True, comment="文件大小(字节)")

    # 解析状态
    is_downloaded = Column(Boolean, default=False, nullable=False, comment="是否已下载")
    is_parsed = Column(Boolean, default=False, nullable=False, comment="是否已解析")
    parsed_content = Column(Text, nullable=True, comment="解析后的文本内容")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    contest = relationship("Contest", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<ContestAttachment(id={self.id}, name={self.name}, contest_id={self.contest_id})>"


class UserContestTag(Base):
    """用户赛事标签（用于个性化推荐）"""
    __tablename__ = "user_contest_tags"

    id = Column(String(50), primary_key=True, comment="ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    tag = Column(String(50), nullable=False, index=True, comment="标签")
    weight = Column(Integer, default=1, nullable=False, comment="权重")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<UserContestTag(user_id={self.user_id}, tag={self.tag}, weight={self.weight})>"


class ContestComment(Base):
    """赛事评论表"""
    __tablename__ = "contest_comments"

    id = Column(String(50), primary_key=True, comment="评论ID")
    contest_id = Column(String(50), ForeignKey("contests.id"), nullable=False, index=True, comment="赛事ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="评论用户ID")
    parent_id = Column(String(50), ForeignKey("contest_comments.id"), nullable=True, index=True, comment="父评论ID（用于回复）")

    content = Column(Text, nullable=False, comment="评论内容")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    is_pinned = Column(Boolean, default=False, nullable=False, comment="是否置顶")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    contest = relationship("Contest")
    user = relationship("User", foreign_keys=[user_id])
    parent = relationship("ContestComment", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<ContestComment(id={self.id}, contest_id={self.contest_id}, user_id={self.user_id})>"


class PrivateMessage(Base):
    """用户私信表"""
    __tablename__ = "private_messages"

    id = Column(String(50), primary_key=True, comment="消息ID")
    sender_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="发送者ID")
    receiver_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True, comment="接收者ID")

    content = Column(Text, nullable=False, comment="消息内容")
    is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
    is_deleted_by_sender = Column(Boolean, default=False, nullable=False, comment="发送者是否删除")
    is_deleted_by_receiver = Column(Boolean, default=False, nullable=False, comment="接收者是否删除")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    def __repr__(self) -> str:
        return f"<PrivateMessage(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id})>"
