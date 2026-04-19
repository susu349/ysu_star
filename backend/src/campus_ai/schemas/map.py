"""
地图打卡模块 Schema
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from campus_ai.models.map import (
    POIType, POIStatus, CheckInVisibility
)


# ============== POI 相关 ==============

class POIBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="地点名称")
    description: Optional[str] = Field(None, description="地点描述")
    poi_type: str = Field("other", description="地点类型")

    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    tile_x: Optional[int] = Field(None, description="瓦片X坐标")
    tile_y: Optional[int] = Field(None, description="瓦片Y坐标")
    zoom_level: Optional[int] = Field(18, description="缩放级别")

    address: Optional[str] = Field(None, max_length=500, description="详细地址")
    building_number: Optional[str] = Field(None, max_length=100, description="楼号")

    cover_image: Optional[str] = Field(None, description="封面图片URL")
    images: Optional[List[str]] = Field(default_factory=list, description="图片URL列表")

    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    categories: Optional[List[str]] = Field(default_factory=list, description="分类列表")

    opening_hours: Optional[str] = Field(None, max_length=200, description="开放时间")
    contact_info: Optional[str] = Field(None, max_length=200, description="联系方式")
    extra_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展信息")


class POICreate(POIBase):
    pass


class POIUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    poi_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tile_x: Optional[int] = None
    tile_y: Optional[int] = None
    zoom_level: Optional[int] = None
    address: Optional[str] = Field(None, max_length=500)
    building_number: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    opening_hours: Optional[str] = Field(None, max_length=200)
    contact_info: Optional[str] = Field(None, max_length=200)
    extra_info: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class POIResponse(POIBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    reject_reason: Optional[str] = None

    check_in_count: int
    like_count: int
    favorite_count: int
    comment_count: int
    view_count: int

    creator_id: Optional[str] = None
    is_official: bool

    created_at: datetime
    updated_at: datetime


class POIListResponse(BaseModel):
    total: int
    items: List[POIResponse]


class POIWithDistanceResponse(POIResponse):
    distance: Optional[float] = None


# ============== 打卡相关 ==============

class CheckInBase(BaseModel):
    content: Optional[str] = Field(None, description="打卡文字内容")
    images: Optional[List[str]] = Field(default_factory=list, description="打卡图片URL列表")

    latitude: Optional[float] = Field(None, description="打卡纬度")
    longitude: Optional[float] = Field(None, description="打卡经度")
    location_name: Optional[str] = Field(None, max_length=200, description="自定义位置名称")

    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    topics: Optional[List[str]] = Field(default_factory=list, description="话题")

    visibility: str = Field("public", description="可见性")


class CheckInCreate(CheckInBase):
    poi_id: str = Field(..., description="POI ID")


class CheckInUpdate(BaseModel):
    content: Optional[str] = None
    images: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    visibility: Optional[str] = None
    is_pinned: Optional[bool] = None


class CheckInResponse(CheckInBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    poi_id: str
    user_id: str

    like_count: int
    comment_count: int
    share_count: int

    is_active: bool
    is_pinned: bool

    created_at: datetime
    updated_at: datetime


class CheckInListResponse(BaseModel):
    total: int
    items: List[CheckInResponse]


class CheckInWithUserResponse(CheckInResponse):
    user: Optional[Dict[str, Any]] = None
    poi: Optional[POIResponse] = None


# ============== POI 评论相关 ==============

class POICommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    images: Optional[List[str]] = Field(default_factory=list, description="图片URL列表")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")
    parent_id: Optional[str] = Field(None, description="回复的评论ID")


class POICommentCreate(POICommentBase):
    poi_id: str = Field(..., description="POI ID")


class POICommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    images: Optional[List[str]] = None


class POICommentResponse(POICommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    poi_id: str
    user_id: str
    like_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class POICommentListResponse(BaseModel):
    total: int
    items: List[POICommentResponse]


# ============== 打卡评论相关 ==============

class CheckInCommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    images: Optional[List[str]] = Field(default_factory=list, description="图片URL列表")
    parent_id: Optional[str] = Field(None, description="回复的评论ID")


class CheckInCommentCreate(CheckInCommentBase):
    check_in_id: str = Field(..., description="打卡ID")


class CheckInCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    images: Optional[List[str]] = None


class CheckInCommentResponse(CheckInCommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    check_in_id: str
    user_id: str
    like_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CheckInCommentListResponse(BaseModel):
    total: int
    items: List[CheckInCommentResponse]


# ============== 收藏相关 ==============

class UserFavoritePOICreate(BaseModel):
    poi_id: str = Field(..., description="POI ID")
    note: Optional[str] = Field(None, max_length=500, description="收藏备注")


class UserFavoritePOIResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    poi_id: str
    user_id: str
    note: Optional[str] = None
    created_at: datetime


class UserFavoritePOIListResponse(BaseModel):
    total: int
    items: List[UserFavoritePOIResponse]


# ============== 话题相关 ==============

class MapTopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="话题名称")
    description: Optional[str] = Field(None, description="话题描述")
    cover_image: Optional[str] = Field(None, description="话题封面")
    color: Optional[str] = Field(None, max_length=20, description="话题颜色")


class MapTopicCreate(MapTopicBase):
    pass


class MapTopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    is_hot: Optional[bool] = None


class MapTopicResponse(MapTopicBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    check_in_count: int
    follower_count: int
    is_active: bool
    is_hot: bool
    creator_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MapTopicListResponse(BaseModel):
    total: int
    items: List[MapTopicResponse]


# ============== 查询参数 ==============

class POISearchQuery(BaseModel):
    keyword: Optional[str] = Field(None, description="搜索关键词")
    poi_type: Optional[str] = Field(None, description="地点类型")
    tags: Optional[List[str]] = Field(None, description="标签")
    lat_min: Optional[float] = Field(None, description="最小纬度")
    lat_max: Optional[float] = Field(None, description="最大纬度")
    lng_min: Optional[float] = Field(None, description="最小经度")
    lng_max: Optional[float] = Field(None, description="最大经度")
    status: Optional[str] = Field("approved", description="状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field("check_in_count", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")


class CheckInQuery(BaseModel):
    poi_id: Optional[str] = Field(None, description="POI ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    topic: Optional[str] = Field(None, description="话题")
    visibility: Optional[str] = Field("public", description="可见性")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")


# ============== 统计相关 ==============

class MapStatsResponse(BaseModel):
    total_pois: int
    total_check_ins: int
    total_users: int
    total_topics: int
    hot_pois: List[POIResponse]
    hot_topics: List[MapTopicResponse]
    recent_check_ins: List[CheckInResponse]
