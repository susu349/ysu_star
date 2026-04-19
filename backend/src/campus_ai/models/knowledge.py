"""
知识库相关数据模型
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class KnowledgeStatus(str, enum.Enum):
    """知识状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    APPROVED = "approved"     # 已通过
    REJECTED = "rejected"     # 已拒绝


class KnowledgeSource(str, enum.Enum):
    """数据来源"""
    MANUAL = "manual"         # 手动录入
    UPLOAD = "upload"         # 文件上传
    CRAWLER = "crawler"       # 爬虫采集
    USER = "user"             # 用户贡献


class KnowledgeCategory(str, enum.Enum):
    """知识分类（对应知识库目录）"""
    # 基础校园数据
    SCHOOL_HISTORY = "school_history"           # 校史校情
    RULES = "rules"                             # 规章制度
    DEPARTMENTS = "departments"                 # 院系专业
    MAP = "map"                                 # 校园地图
    COURSES = "courses"                         # 教学资源

    # 学习资源
    LEARNING_MATERIALS = "learning_materials"   # 学习资料
    CONTESTS = "contests"                       # 竞赛库
    POSTGRADUATE = "postgraduate"               # 考研保研

    # 生活服务
    DAILY = "daily"                             # 日常（吃喝玩乐）
    DORM = "dorm"                               # 宿舍
    EXPRESS = "express"                         # 快递

    # 互动内容
    EXPERIENCE = "experience"                   # 经验分享
    QA = "qa"                                   # Q&A问答
    CLUBS = "clubs"                             # 社团
    SENIOR_MESSAGE = "senior_message"           # 学长留言
    PROJECTS = "projects"                       # 项目课题
    JOBS = "jobs"                               # 工作分享
    TECH_RECOMMEND = "tech_recommend"           # 黑科技推荐


class KnowledgeDocument(Base):
    """知识文档主表"""
    __tablename__ = "knowledge_documents"

    id = Column(String(50), primary_key=True, comment="文档ID")
    title = Column(String(255), nullable=False, index=True, comment="文档标题")
    summary = Column(Text, nullable=True, comment="文档摘要")
    content = Column(Text, nullable=True, comment="文档内容（纯文本）")
    category = Column(String(50), nullable=False, index=True, comment="分类")
    tags = Column(JSON, nullable=True, default=list, comment="标签列表")

    # 来源信息
    source = Column(String(20), nullable=False, comment="数据来源")
    source_url = Column(String(500), nullable=True, comment="来源URL（爬虫用）")
    source_file = Column(String(255), nullable=True, comment="源文件路径")

    # 元数据
    author = Column(String(100), nullable=True, comment="作者/提交者")
    submitter_id = Column(String(50), ForeignKey("users.id"), nullable=True, comment="提交用户ID")
    status = Column(String(20), nullable=False, default="draft", comment="状态")

    # 版本控制
    version = Column(Integer, default=1, nullable=False, comment="版本号")
    parent_id = Column(String(50), nullable=True, comment="父文档ID（用于修订）")

    # 权限
    permission = Column(String(20), nullable=False, default="everyone", comment="权限：everyone/registered/admin")

    # 统计
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")
    use_count = Column(Integer, default=0, nullable=False, comment="被AI引用次数")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")

    # 时间
    published_at = Column(DateTime(timezone=True), nullable=True, comment="发布时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")
    submitter = relationship("User", foreign_keys=[submitter_id])

    def __repr__(self) -> str:
        return f"<KnowledgeDocument(id={self.id}, title={self.title}, category={self.category})>"


class KnowledgeChunk(Base):
    """知识文本分块表（用于RAG）"""
    __tablename__ = "knowledge_chunks"

    id = Column(String(50), primary_key=True, comment="分块ID")
    document_id = Column(String(50), ForeignKey("knowledge_documents.id"), nullable=False, index=True, comment="文档ID")
    chunk_index = Column(Integer, nullable=False, comment="在文档中的序号")

    content = Column(Text, nullable=False, comment="分块内容")
    content_hash = Column(String(64), nullable=False, comment="内容哈希（用于去重）")

    # 向量信息
    vector_id = Column(String(50), nullable=True, index=True, comment="Milvus中的向量ID")
    embedding_model = Column(String(100), nullable=True, comment="使用的嵌入模型")

    # 分块特性
    chunk_type = Column(String(20), nullable=True, comment="分块类型：text/table/image")
    meta = Column(JSON, nullable=True, default=dict, comment="额外元数据")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    document = relationship("KnowledgeDocument", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<KnowledgeChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"


class DataSource(Base):
    """数据源管理表"""
    __tablename__ = "data_sources"

    id = Column(String(50), primary_key=True, comment="数据源ID")
    name = Column(String(100), nullable=False, comment="数据源名称")
    source_type = Column(String(20), nullable=False, comment="类型：website/file/api")

    # 爬虫配置
    base_url = Column(String(500), nullable=True, comment="基础URL")
    crawl_config = Column(JSON, nullable=True, default=dict, comment="爬虫配置（选择器、延迟等）")
    last_crawled_at = Column(DateTime(timezone=True), nullable=True, comment="最后爬取时间")

    # 文件源配置
    file_path = Column(String(255), nullable=True, comment="文件路径")
    file_pattern = Column(String(100), nullable=True, comment="文件匹配模式")

    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name={self.name})>"


class CrawlTask(Base):
    """爬虫任务表"""
    __tablename__ = "crawl_tasks"

    id = Column(String(50), primary_key=True, comment="任务ID")
    source_id = Column(String(50), ForeignKey("data_sources.id"), nullable=False, comment="数据源ID")
    status = Column(String(20), nullable=False, default="pending", comment="状态：pending/running/completed/failed")

    url = Column(String(500), nullable=True, comment="目标URL")
    config = Column(JSON, nullable=True, default=dict, comment="任务配置")

    # 统计
    pages_found = Column(Integer, default=0, nullable=False, comment="发现页面数")
    pages_processed = Column(Integer, default=0, nullable=False, comment="处理页面数")
    docs_created = Column(Integer, default=0, nullable=False, comment="创建文档数")

    error_message = Column(Text, nullable=True, comment="错误信息")

    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    def __repr__(self) -> str:
        return f"<CrawlTask(id={self.id}, status={self.status})>"


class UserContribution(Base):
    """用户贡献表"""
    __tablename__ = "user_contributions"

    id = Column(String(50), primary_key=True, comment="贡献ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")
    document_id = Column(String(50), ForeignKey("knowledge_documents.id"), nullable=True, comment="关联文档ID")

    contribution_type = Column(String(20), nullable=False, comment="贡献类型：document/edit/like")
    points = Column(Integer, default=0, nullable=False, comment="获得积分")

    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<UserContribution(id={self.id}, user_id={self.user_id})>"
