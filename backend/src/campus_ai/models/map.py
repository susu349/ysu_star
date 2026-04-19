from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, Float, Enum, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class POIType(enum.Enum):
    """兴趣点类型"""
    BUILDING = "building"      # 建筑
    LANDSCAPE = "landscape"    # 风景
    FOOD = "food"              # 美食
    FACILITY = "facility"      # 设施
    OTHER = "other"            # 其他


class POIStatus(enum.Enum):
    """POI状态"""
    PENDING = "pending"        # 待审核
    APPROVED = "approved"      # 已通过
    REJECTED = "rejected"      # 已拒绝


class CheckInVisibility(enum.Enum):
    """打卡可见性"""
    PUBLIC = "public"          # 公开
    FRIENDS = "friends"        # 仅好友
    PRIVATE = "private"        # 私密


class POI(Base):
    """兴趣点（地点）模型"""
    __tablename__ = "map_pois"

    id = Column(String(50), primary_key=True, comment="POI ID")
    name = Column(String(200), nullable=False, comment="地点名称")
    description = Column(Text, nullable=True, comment="地点描述")
    poi_type = Column(String(50), nullable=False, default="other", comment="地点类型")

    # 坐标信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    tile_x = Column(Integer, nullable=True, comment="瓦片X坐标")
    tile_y = Column(Integer, nullable=True, comment="瓦片Y坐标")
    zoom_level = Column(Integer, nullable=True, default=18, comment="缩放级别")

    # 地址信息
    address = Column(String(500), nullable=True, comment="详细地址")
    building_number = Column(String(100), nullable=True, comment="楼号")

    # 媒体信息
    cover_image = Column(String(255), nullable=True, comment="封面图片URL")
    images = Column(JSON, nullable=True, default=list, comment="图片URL列表")

    # 标签和分类
    tags = Column(JSON, nullable=True, default=list, comment="标签列表")
    categories = Column(JSON, nullable=True, default=list, comment="分类列表")

    # 统计信息
    check_in_count = Column(Integer, default=0, nullable=False, comment="打卡次数")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    favorite_count = Column(Integer, default=0, nullable=False, comment="收藏数")
    comment_count = Column(Integer, default=0, nullable=False, comment="评论数")
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")

    # 附加信息
    opening_hours = Column(String(200), nullable=True, comment="开放时间")
    contact_info = Column(String(200), nullable=True, comment="联系方式")
    extra_info = Column(JSON, nullable=True, default=dict, comment="扩展信息")

    # 审核状态
    status = Column(String(50), nullable=False, default="approved", comment="状态")
    reject_reason = Column(Text, nullable=True, comment="拒绝原因")

    # 创建者信息
    creator_id = Column(String(50), ForeignKey("users.id"), nullable=True, comment="创建者ID")
    is_official = Column(Boolean, default=False, nullable=False, comment="是否官方创建")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    creator = relationship("User", backref="created_pois")
    check_ins = relationship("CheckIn", back_populates="poi", cascade="all, delete-orphan")
    comments = relationship("POIComment", back_populates="poi", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<POI(id={self.id}, name={self.name}, type={self.poi_type})>"


class CheckIn(Base):
    """打卡记录模型"""
    __tablename__ = "map_check_ins"

    id = Column(String(50), primary_key=True, comment="打卡ID")

    # 关联信息
    poi_id = Column(String(50), ForeignKey("map_pois.id"), nullable=False, comment="POI ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")

    # 打卡内容
    content = Column(Text, nullable=True, comment="打卡文字内容")
    images = Column(JSON, nullable=True, default=list, comment="打卡图片URL列表")

    # 位置信息（可以是POI位置，也可以自定义）
    latitude = Column(Float, nullable=True, comment="打卡纬度")
    longitude = Column(Float, nullable=True, comment="打卡经度")
    location_name = Column(String(200), nullable=True, comment="自定义位置名称")

    # 标签和话题
    tags = Column(JSON, nullable=True, default=list, comment="标签")
    topics = Column(JSON, nullable=True, default=list, comment="话题")

    # 可见性设置
    visibility = Column(String(50), nullable=False, default="public", comment="可见性")

    # 互动统计
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    comment_count = Column(Integer, default=0, nullable=False, comment="评论数")
    share_count = Column(Integer, default=0, nullable=False, comment="分享数")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否显示")
    is_pinned = Column(Boolean, default=False, nullable=False, comment="是否置顶")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="打卡时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    poi = relationship("POI", back_populates="check_ins")
    user = relationship("User", backref="check_ins")
    comments = relationship("CheckInComment", back_populates="check_in", cascade="all, delete-orphan")
    likes = relationship("CheckInLike", back_populates="check_in", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, poi_id={self.poi_id})>"


class POIComment(Base):
    """POI评论模型"""
    __tablename__ = "map_poi_comments"

    id = Column(String(50), primary_key=True, comment="评论ID")
    poi_id = Column(String(50), ForeignKey("map_pois.id"), nullable=False, comment="POI ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")

    content = Column(Text, nullable=False, comment="评论内容")
    images = Column(JSON, nullable=True, default=list, comment="图片URL列表")

    rating = Column(Integer, nullable=True, comment="评分(1-5)")
    parent_id = Column(String(50), ForeignKey("map_poi_comments.id"), nullable=True, comment="回复的评论ID")

    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否显示")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    poi = relationship("POI", back_populates="comments")
    user = relationship("User", backref="poi_comments")
    parent = relationship("POIComment", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<POIComment(id={self.id}, poi_id={self.poi_id})>"


class CheckInComment(Base):
    """打卡评论模型"""
    __tablename__ = "map_check_in_comments"

    id = Column(String(50), primary_key=True, comment="评论ID")
    check_in_id = Column(String(50), ForeignKey("map_check_ins.id"), nullable=False, comment="打卡ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")

    content = Column(Text, nullable=False, comment="评论内容")
    images = Column(JSON, nullable=True, default=list, comment="图片URL列表")

    parent_id = Column(String(50), ForeignKey("map_check_in_comments.id"), nullable=True, comment="回复的评论ID")

    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否显示")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    check_in = relationship("CheckIn", back_populates="comments")
    user = relationship("User", backref="check_in_comments")
    parent = relationship("CheckInComment", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<CheckInComment(id={self.id}, check_in_id={self.check_in_id})>"


class CheckInLike(Base):
    """打卡点赞模型"""
    __tablename__ = "map_check_in_likes"

    id = Column(String(50), primary_key=True, comment="点赞ID")
    check_in_id = Column(String(50), ForeignKey("map_check_ins.id"), nullable=False, comment="打卡ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="点赞时间")

    check_in = relationship("CheckIn", back_populates="likes")
    user = relationship("User", backref="check_in_likes")

    __table_args__ = (
        UniqueConstraint('check_in_id', 'user_id', name='uix_check_in_user'),
    )


class UserFavoritePOI(Base):
    """用户收藏POI模型"""
    __tablename__ = "map_user_favorite_pois"

    id = Column(String(50), primary_key=True, comment="收藏ID")
    poi_id = Column(String(50), ForeignKey("map_pois.id"), nullable=False, comment="POI ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")

    note = Column(String(500), nullable=True, comment="收藏备注")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="收藏时间")

    poi = relationship("POI", backref="favorited_by")
    user = relationship("User", backref="favorite_pois")

    __table_args__ = (
        UniqueConstraint('poi_id', 'user_id', name='uix_poi_user'),
    )


class MapTopic(Base):
    """地图话题模型"""
    __tablename__ = "map_topics"

    id = Column(String(50), primary_key=True, comment="话题ID")
    name = Column(String(100), unique=True, nullable=False, comment="话题名称")
    description = Column(Text, nullable=True, comment="话题描述")

    cover_image = Column(String(255), nullable=True, comment="话题封面")
    color = Column(String(20), nullable=True, comment="话题颜色")

    check_in_count = Column(Integer, default=0, nullable=False, comment="打卡数")
    follower_count = Column(Integer, default=0, nullable=False, comment="关注数")

    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    is_hot = Column(Boolean, default=False, nullable=False, comment="是否热门")

    creator_id = Column(String(50), ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    creator = relationship("User", backref="created_topics")

    def __repr__(self) -> str:
        return f"<MapTopic(id={self.id}, name={self.name})>"
