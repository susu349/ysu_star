"""
地图打卡模块 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_active_user
from ...models.user import User
from ...models.map import (
    POI, CheckIn, POIComment, CheckInComment
)
from ...schemas.map import (
    POICreate, POIUpdate, POIResponse, POIListResponse,
    CheckInCreate, CheckInUpdate, CheckInResponse, CheckInListResponse,
    POICommentCreate, POICommentUpdate, POICommentResponse, POICommentListResponse,
    CheckInCommentCreate, CheckInCommentUpdate, CheckInCommentResponse, CheckInCommentListResponse,
    MapTopicCreate, MapTopicUpdate, MapTopicResponse, MapTopicListResponse,
    UserFavoritePOICreate, UserFavoritePOIResponse, UserFavoritePOIListResponse,
    POISearchQuery, CheckInQuery, MapStatsResponse, CheckInWithUserResponse
)
from ...services.map_service import (
    POIService, CheckInService, CheckInLikeService,
    POICommentService, CheckInCommentService,
    FavoriteService, TopicService, MapStatsService
)
from ...services.contest.storage_service import StorageService

router = APIRouter(prefix="/map", tags=["智慧地图"])


# ============== POI 相关接口 ==============

@router.get("/pois", response_model=POIListResponse)
def list_pois(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    poi_type: Optional[str] = Query(None, description="地点类型"),
    tags: Optional[str] = Query(None, description="标签（逗号分隔）"),
    lat_min: Optional[float] = Query(None, description="最小纬度"),
    lat_max: Optional[float] = Query(None, description="最大纬度"),
    lng_min: Optional[float] = Query(None, description="最小经度"),
    lng_max: Optional[float] = Query(None, description="最大经度"),
    status: Optional[str] = Query("approved", description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: Optional[str] = Query("check_in_count", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    db: Session = Depends(get_db)
):
    """获取POI列表"""
    tag_list = tags.split(",") if tags else None
    skip = (page - 1) * page_size

    pois, total = POIService.list_pois(
        db,
        keyword=keyword,
        poi_type=poi_type,
        tags=tag_list,
        lat_min=lat_min,
        lat_max=lat_max,
        lng_min=lng_min,
        lng_max=lng_max,
        status=status,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {"total": total, "items": pois}


@router.get("/pois/hot", response_model=POIListResponse)
def get_hot_pois(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db)
):
    """获取热门POI"""
    pois = POIService.get_hot_pois(db, limit=limit)
    return {"total": len(pois), "items": pois}


@router.get("/pois/{poi_id}", response_model=POIResponse)
def get_poi(
    poi_id: str,
    db: Session = Depends(get_db)
):
    """获取POI详情"""
    poi = POIService.get_poi_by_id(db, poi_id)
    if not poi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地点不存在"
        )
    POIService.increment_view_count(db, poi)
    return poi


@router.post("/pois", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
def create_poi(
    poi_data: POICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建POI"""
    return POIService.create_poi(db, poi_data, creator_id=current_user.id)


@router.put("/pois/{poi_id}", response_model=POIResponse)
def update_poi(
    poi_id: str,
    poi_data: POIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新POI"""
    poi = POIService.get_poi_by_id(db, poi_id)
    if not poi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地点不存在"
        )
    if poi.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改"
        )
    return POIService.update_poi(db, poi, poi_data)


@router.delete("/pois/{poi_id}", status_code=status.HTTP_200_OK)
def delete_poi(
    poi_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除POI"""
    poi = POIService.get_poi_by_id(db, poi_id)
    if not poi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地点不存在"
        )
    if poi.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除"
        )
    POIService.delete_poi(db, poi)
    return {"message": "删除成功"}


# ============== 打卡相关接口 ==============

@router.get("/check-ins", response_model=CheckInListResponse)
def list_check_ins(
    poi_id: Optional[str] = Query(None, description="POI ID"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    topic: Optional[str] = Query(None, description="话题"),
    visibility: Optional[str] = Query("public", description="可见性"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    db: Session = Depends(get_db)
):
    """获取打卡列表"""
    skip = (page - 1) * page_size
    check_ins, total = CheckInService.list_check_ins(
        db,
        poi_id=poi_id,
        user_id=user_id,
        topic=topic,
        visibility=visibility,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {"total": total, "items": check_ins}


@router.get("/check-ins/recent", response_model=CheckInListResponse)
def get_recent_check_ins(
    limit: int = Query(20, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db)
):
    """获取最新打卡"""
    check_ins = CheckInService.get_recent_check_ins(db, limit=limit)
    return {"total": len(check_ins), "items": check_ins}


@router.get("/check-ins/{check_in_id}", response_model=CheckInResponse)
def get_check_in(
    check_in_id: str,
    db: Session = Depends(get_db)
):
    """获取打卡详情"""
    check_in = CheckInService.get_check_in_by_id(db, check_in_id)
    if not check_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="打卡不存在"
        )
    return check_in


@router.post("/check-ins", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_check_in(
    check_in_data: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建打卡"""
    return CheckInService.create_check_in(db, check_in_data, user_id=current_user.id)


@router.put("/check-ins/{check_in_id}", response_model=CheckInResponse)
def update_check_in(
    check_in_id: str,
    check_in_data: CheckInUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新打卡"""
    check_in = CheckInService.get_check_in_by_id(db, check_in_id)
    if not check_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="打卡不存在"
        )
    if check_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改"
        )
    return CheckInService.update_check_in(db, check_in, check_in_data)


@router.delete("/check-ins/{check_in_id}", status_code=status.HTTP_200_OK)
def delete_check_in(
    check_in_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除打卡"""
    check_in = CheckInService.get_check_in_by_id(db, check_in_id)
    if not check_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="打卡不存在"
        )
    if check_in.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除"
        )
    CheckInService.delete_check_in(db, check_in)
    return {"message": "删除成功"}


@router.post("/check-ins/{check_in_id}/like", status_code=status.HTTP_200_OK)
def toggle_check_in_like(
    check_in_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """打卡点赞/取消点赞"""
    liked, like_count = CheckInLikeService.toggle_like(db, check_in_id, current_user.id)
    return {"liked": liked, "like_count": like_count}


@router.get("/check-ins/{check_in_id}/has-liked", status_code=status.HTTP_200_OK)
def has_liked_check_in(
    check_in_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查是否已点赞"""
    has_liked = CheckInLikeService.has_liked(db, check_in_id, current_user.id)
    return {"has_liked": has_liked}


# ============== POI 评论接口 ==============

@router.get("/pois/{poi_id}/comments", response_model=POICommentListResponse)
def list_poi_comments(
    poi_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取POI评论列表"""
    skip = (page - 1) * page_size
    comments, total = POICommentService.list_comments(db, poi_id, skip=skip, limit=page_size)
    return {"total": total, "items": comments}


@router.post("/pois/{poi_id}/comments", response_model=POICommentResponse, status_code=status.HTTP_201_CREATED)
def create_poi_comment(
    poi_id: str,
    comment_data: POICommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建POI评论"""
    comment_data.poi_id = poi_id
    return POICommentService.create_comment(db, comment_data, user_id=current_user.id)


@router.put("/poi-comments/{comment_id}", response_model=POICommentResponse)
def update_poi_comment(
    comment_id: str,
    comment_data: POICommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新POI评论"""
    comment = POICommentService.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改"
        )
    return POICommentService.update_comment(db, comment, comment_data)


@router.delete("/poi-comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_poi_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除POI评论"""
    comment = POICommentService.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除"
        )
    POICommentService.delete_comment(db, comment)
    return {"message": "删除成功"}


# ============== 打卡评论接口 ==============

@router.get("/check-ins/{check_in_id}/comments", response_model=CheckInCommentListResponse)
def list_check_in_comments(
    check_in_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取打卡评论列表"""
    skip = (page - 1) * page_size
    comments, total = CheckInCommentService.list_comments(db, check_in_id, skip=skip, limit=page_size)
    return {"total": total, "items": comments}


@router.post("/check-ins/{check_in_id}/comments", response_model=CheckInCommentResponse, status_code=status.HTTP_201_CREATED)
def create_check_in_comment(
    check_in_id: str,
    comment_data: CheckInCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建打卡评论"""
    comment_data.check_in_id = check_in_id
    return CheckInCommentService.create_comment(db, comment_data, user_id=current_user.id)


@router.put("/check-in-comments/{comment_id}", response_model=CheckInCommentResponse)
def update_check_in_comment(
    comment_id: str,
    comment_data: CheckInCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新打卡评论"""
    comment = CheckInCommentService.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改"
        )
    return CheckInCommentService.update_comment(db, comment, comment_data)


@router.delete("/check-in-comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_check_in_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除打卡评论"""
    comment = CheckInCommentService.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除"
        )
    CheckInCommentService.delete_comment(db, comment)
    return {"message": "删除成功"}


# ============== 收藏接口 ==============

@router.get("/favorites", response_model=UserFavoritePOIListResponse)
def list_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户收藏列表"""
    skip = (page - 1) * page_size
    favorites, total = FavoriteService.list_user_favorites(db, current_user.id, skip=skip, limit=page_size)
    return {"total": total, "items": favorites}


@router.post("/favorites/toggle", status_code=status.HTTP_200_OK)
def toggle_favorite(
    favorite_data: UserFavoritePOICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """收藏/取消收藏"""
    favorited, favorite_count = FavoriteService.toggle_favorite(db, favorite_data, current_user.id)
    return {"favorited": favorited, "favorite_count": favorite_count}


@router.get("/pois/{poi_id}/has-favorited", status_code=status.HTTP_200_OK)
def has_favorited(
    poi_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查是否已收藏"""
    has_favorited = FavoriteService.has_favorited(db, poi_id, current_user.id)
    return {"has_favorited": has_favorited}


# ============== 话题接口 ==============

@router.get("/topics", response_model=MapTopicListResponse)
def list_topics(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取话题列表"""
    skip = (page - 1) * page_size
    topics, total = TopicService.list_topics(db, skip=skip, limit=page_size)
    return {"total": total, "items": topics}


@router.get("/topics/hot", response_model=MapTopicListResponse)
def get_hot_topics(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db)
):
    """获取热门话题"""
    topics = TopicService.get_hot_topics(db, limit=limit)
    return {"total": len(topics), "items": topics}


@router.get("/topics/{topic_id}", response_model=MapTopicResponse)
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db)
):
    """获取话题详情"""
    topic = TopicService.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="话题不存在"
        )
    return topic


@router.post("/topics", response_model=MapTopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_data: MapTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建话题"""
    return TopicService.create_topic(db, topic_data, creator_id=current_user.id)


@router.put("/topics/{topic_id}", response_model=MapTopicResponse)
def update_topic(
    topic_id: str,
    topic_data: MapTopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新话题"""
    topic = TopicService.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="话题不存在"
        )
    if topic.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改"
        )
    return TopicService.update_topic(db, topic, topic_data)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_200_OK)
def delete_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除话题"""
    topic = TopicService.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="话题不存在"
        )
    if topic.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除"
        )
    TopicService.delete_topic(db, topic)
    return {"message": "删除成功"}


# ============== 统计接口 ==============

@router.get("/stats", response_model=dict)
def get_map_stats(db: Session = Depends(get_db)):
    """获取地图统计数据"""
    return MapStatsService.get_stats(db)


# ============== 图片上传接口 ==============

@router.post("/upload-image", status_code=status.HTTP_200_OK)
async def upload_map_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """上传地图相关图片"""
    url = await StorageService.save_upload_file(file, "map")
    return {"url": url}
