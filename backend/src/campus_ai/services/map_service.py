"""
地图打卡模块 Service
"""
import uuid
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc, func
from fastapi import HTTPException, status

from ..models.map import (
    POI, CheckIn, POIComment, CheckInComment,
    CheckInLike, UserFavoritePOI, MapTopic, POIStatus
)
from ..models.user import User
from ..schemas.map import (
    POICreate, POIUpdate, CheckInCreate, CheckInUpdate,
    POICommentCreate, POICommentUpdate, CheckInCommentCreate, CheckInCommentUpdate,
    MapTopicCreate, MapTopicUpdate, UserFavoritePOICreate
)


class POIService:
    """POI服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_poi_by_id(db: Session, poi_id: str) -> Optional[POI]:
        return db.query(POI).filter(POI.id == poi_id).first()

    @staticmethod
    def create_poi(db: Session, poi_data: POICreate, creator_id: Optional[str] = None) -> POI:
        poi_id = POIService.generate_id()
        db_poi = POI(
            id=poi_id,
            **poi_data.model_dump(),
            creator_id=creator_id,
            is_official=creator_id is None,
            status="pending" if creator_id else "approved"
        )
        db.add(db_poi)
        db.commit()
        db.refresh(db_poi)
        return db_poi

    @staticmethod
    def update_poi(db: Session, poi: POI, poi_data: POIUpdate) -> POI:
        update_data = poi_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(poi, field, value)
        db.commit()
        db.refresh(poi)
        return poi

    @staticmethod
    def delete_poi(db: Session, poi: POI) -> None:
        db.delete(poi)
        db.commit()

    @staticmethod
    def increment_view_count(db: Session, poi: POI) -> None:
        poi.view_count += 1
        db.commit()

    @staticmethod
    def increment_check_in_count(db: Session, poi: POI) -> None:
        poi.check_in_count += 1
        db.commit()

    @staticmethod
    def list_pois(
        db: Session,
        keyword: Optional[str] = None,
        poi_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lat_min: Optional[float] = None,
        lat_max: Optional[float] = None,
        lng_min: Optional[float] = None,
        lng_max: Optional[float] = None,
        status: Optional[str] = "approved",
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = "check_in_count",
        sort_order: Optional[str] = "desc"
    ) -> Tuple[List[POI], int]:
        query = db.query(POI)

        if status:
            query = query.filter(POI.status == status)

        if keyword:
            query = query.filter(
                or_(
                    POI.name.contains(keyword),
                    POI.description.contains(keyword)
                )
            )

        if poi_type:
            query = query.filter(POI.poi_type == poi_type)

        if tags:
            for tag in tags:
                query = query.filter(POI.tags.contains([tag]))

        if lat_min and lat_max:
            query = query.filter(POI.latitude.between(lat_min, lat_max))
        if lng_min and lng_max:
            query = query.filter(POI.longitude.between(lng_min, lng_max))

        total = query.count()

        if sort_by:
            order_func = desc if sort_order == "desc" else asc
            if hasattr(POI, sort_by):
                query = query.order_by(order_func(getattr(POI, sort_by)))

        pois = query.offset(skip).limit(limit).all()
        return pois, total

    @staticmethod
    def get_hot_pois(db: Session, limit: int = 10) -> List[POI]:
        return (
            db.query(POI)
            .filter(POI.status == "approved")
            .order_by(desc(POI.check_in_count))
            .limit(limit)
            .all()
        )


class CheckInService:
    """打卡服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_check_in_by_id(db: Session, check_in_id: str) -> Optional[CheckIn]:
        return db.query(CheckIn).filter(CheckIn.id == check_in_id).first()

    @staticmethod
    def create_check_in(
        db: Session,
        check_in_data: CheckInCreate,
        user_id: str
    ) -> CheckIn:
        poi = POIService.get_poi_by_id(db, check_in_data.poi_id)
        if not poi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地点不存在"
            )

        check_in_id = CheckInService.generate_id()
        db_check_in = CheckIn(
            id=check_in_id,
            **check_in_data.model_dump(),
            user_id=user_id,
            latitude=check_in_data.latitude or poi.latitude,
            longitude=check_in_data.longitude or poi.longitude
        )
        db.add(db_check_in)

        POIService.increment_check_in_count(db, poi)

        if check_in_data.topics:
            for topic_name in check_in_data.topics:
                topic = TopicService.get_topic_by_name(db, topic_name)
                if topic:
                    TopicService.increment_check_in_count(db, topic)

        db.commit()
        db.refresh(db_check_in)
        return db_check_in

    @staticmethod
    def update_check_in(
        db: Session,
        check_in: CheckIn,
        check_in_data: CheckInUpdate
    ) -> CheckIn:
        update_data = check_in_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(check_in, field, value)
        db.commit()
        db.refresh(check_in)
        return check_in

    @staticmethod
    def delete_check_in(db: Session, check_in: CheckIn) -> None:
        poi = POIService.get_poi_by_id(db, check_in.poi_id)
        if poi and poi.check_in_count > 0:
            poi.check_in_count -= 1
        db.delete(check_in)
        db.commit()

    @staticmethod
    def list_check_ins(
        db: Session,
        poi_id: Optional[str] = None,
        user_id: Optional[str] = None,
        topic: Optional[str] = None,
        visibility: Optional[str] = "public",
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc"
    ) -> Tuple[List[CheckIn], int]:
        query = db.query(CheckIn).filter(CheckIn.is_active == True)

        if visibility:
            query = query.filter(CheckIn.visibility == visibility)

        if poi_id:
            query = query.filter(CheckIn.poi_id == poi_id)

        if user_id:
            query = query.filter(CheckIn.user_id == user_id)

        if topic:
            query = query.filter(CheckIn.topics.contains([topic]))

        total = query.count()

        if sort_by:
            order_func = desc if sort_order == "desc" else asc
            if hasattr(CheckIn, sort_by):
                query = query.order_by(order_func(getattr(CheckIn, sort_by)))

        check_ins = query.offset(skip).limit(limit).all()
        return check_ins, total

    @staticmethod
    def get_recent_check_ins(db: Session, limit: int = 20) -> List[CheckIn]:
        return (
            db.query(CheckIn)
            .filter(CheckIn.is_active == True, CheckIn.visibility == "public")
            .order_by(desc(CheckIn.created_at))
            .limit(limit)
            .all()
        )


class CheckInLikeService:
    """打卡点赞服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def toggle_like(
        db: Session,
        check_in_id: str,
        user_id: str
    ) -> Tuple[bool, int]:
        check_in = CheckInService.get_check_in_by_id(db, check_in_id)
        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="打卡不存在"
            )

        existing_like = (
            db.query(CheckInLike)
            .filter(CheckInLike.check_in_id == check_in_id, CheckInLike.user_id == user_id)
            .first()
        )

        if existing_like:
            db.delete(existing_like)
            check_in.like_count = max(0, check_in.like_count - 1)
            liked = False
        else:
            like = CheckInLike(
                id=CheckInLikeService.generate_id(),
                check_in_id=check_in_id,
                user_id=user_id
            )
            db.add(like)
            check_in.like_count += 1
            liked = True

        db.commit()
        return liked, check_in.like_count

    @staticmethod
    def has_liked(db: Session, check_in_id: str, user_id: str) -> bool:
        return (
            db.query(CheckInLike)
            .filter(CheckInLike.check_in_id == check_in_id, CheckInLike.user_id == user_id)
            .first() is not None
        )


class POICommentService:
    """POI评论服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: str) -> Optional[POIComment]:
        return db.query(POIComment).filter(POIComment.id == comment_id).first()

    @staticmethod
    def create_comment(
        db: Session,
        comment_data: POICommentCreate,
        user_id: str
    ) -> POIComment:
        poi = POIService.get_poi_by_id(db, comment_data.poi_id)
        if not poi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地点不存在"
            )

        comment_id = POICommentService.generate_id()
        db_comment = POIComment(
            id=comment_id,
            **comment_data.model_dump(),
            user_id=user_id
        )
        db.add(db_comment)
        poi.comment_count += 1
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def update_comment(
        db: Session,
        comment: POIComment,
        comment_data: POICommentUpdate
    ) -> POIComment:
        update_data = comment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment: POIComment) -> None:
        poi = POIService.get_poi_by_id(db, comment.poi_id)
        if poi and poi.comment_count > 0:
            poi.comment_count -= 1
        db.delete(comment)
        db.commit()

    @staticmethod
    def list_comments(
        db: Session,
        poi_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[POIComment], int]:
        query = (
            db.query(POIComment)
            .filter(POIComment.poi_id == poi_id, POIComment.is_active == True)
            .order_by(desc(POIComment.created_at))
        )
        total = query.count()
        comments = query.offset(skip).limit(limit).all()
        return comments, total


class CheckInCommentService:
    """打卡评论服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: str) -> Optional[CheckInComment]:
        return db.query(CheckInComment).filter(CheckInComment.id == comment_id).first()

    @staticmethod
    def create_comment(
        db: Session,
        comment_data: CheckInCommentCreate,
        user_id: str
    ) -> CheckInComment:
        check_in = CheckInService.get_check_in_by_id(db, comment_data.check_in_id)
        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="打卡不存在"
            )

        comment_id = CheckInCommentService.generate_id()
        db_comment = CheckInComment(
            id=comment_id,
            **comment_data.model_dump(),
            user_id=user_id
        )
        db.add(db_comment)
        check_in.comment_count += 1
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def update_comment(
        db: Session,
        comment: CheckInComment,
        comment_data: CheckInCommentUpdate
    ) -> CheckInComment:
        update_data = comment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment: CheckInComment) -> None:
        check_in = CheckInService.get_check_in_by_id(db, comment.check_in_id)
        if check_in and check_in.comment_count > 0:
            check_in.comment_count -= 1
        db.delete(comment)
        db.commit()

    @staticmethod
    def list_comments(
        db: Session,
        check_in_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[CheckInComment], int]:
        query = (
            db.query(CheckInComment)
            .filter(CheckInComment.check_in_id == check_in_id, CheckInComment.is_active == True)
            .order_by(desc(CheckInComment.created_at))
        )
        total = query.count()
        comments = query.offset(skip).limit(limit).all()
        return comments, total


class FavoriteService:
    """收藏服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_favorite(
        db: Session,
        poi_id: str,
        user_id: str
    ) -> Optional[UserFavoritePOI]:
        return (
            db.query(UserFavoritePOI)
            .filter(UserFavoritePOI.poi_id == poi_id, UserFavoritePOI.user_id == user_id)
            .first()
        )

    @staticmethod
    def toggle_favorite(
        db: Session,
        favorite_data: UserFavoritePOICreate,
        user_id: str
    ) -> Tuple[bool, int]:
        poi = POIService.get_poi_by_id(db, favorite_data.poi_id)
        if not poi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地点不存在"
            )

        existing_favorite = FavoriteService.get_favorite(db, favorite_data.poi_id, user_id)

        if existing_favorite:
            db.delete(existing_favorite)
            poi.favorite_count = max(0, poi.favorite_count - 1)
            favorited = False
        else:
            favorite = UserFavoritePOI(
                id=FavoriteService.generate_id(),
                poi_id=favorite_data.poi_id,
                user_id=user_id,
                note=favorite_data.note
            )
            db.add(favorite)
            poi.favorite_count += 1
            favorited = True

        db.commit()
        return favorited, poi.favorite_count

    @staticmethod
    def has_favorited(db: Session, poi_id: str, user_id: str) -> bool:
        return FavoriteService.get_favorite(db, poi_id, user_id) is not None

    @staticmethod
    def list_user_favorites(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[UserFavoritePOI], int]:
        query = (
            db.query(UserFavoritePOI)
            .filter(UserFavoritePOI.user_id == user_id)
            .order_by(desc(UserFavoritePOI.created_at))
        )
        total = query.count()
        favorites = query.offset(skip).limit(limit).all()
        return favorites, total


class TopicService:
    """话题服务"""

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_topic_by_id(db: Session, topic_id: str) -> Optional[MapTopic]:
        return db.query(MapTopic).filter(MapTopic.id == topic_id).first()

    @staticmethod
    def get_topic_by_name(db: Session, name: str) -> Optional[MapTopic]:
        return db.query(MapTopic).filter(MapTopic.name == name).first()

    @staticmethod
    def create_topic(
        db: Session,
        topic_data: MapTopicCreate,
        creator_id: Optional[str] = None
    ) -> MapTopic:
        existing = TopicService.get_topic_by_name(db, topic_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="话题已存在"
            )

        topic_id = TopicService.generate_id()
        db_topic = MapTopic(
            id=topic_id,
            **topic_data.model_dump(),
            creator_id=creator_id
        )
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic

    @staticmethod
    def update_topic(
        db: Session,
        topic: MapTopic,
        topic_data: MapTopicUpdate
    ) -> MapTopic:
        update_data = topic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def delete_topic(db: Session, topic: MapTopic) -> None:
        topic.is_active = False
        db.commit()

    @staticmethod
    def increment_check_in_count(db: Session, topic: MapTopic) -> None:
        topic.check_in_count += 1
        db.commit()

    @staticmethod
    def list_topics(
        db: Session,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[MapTopic], int]:
        query = db.query(MapTopic)
        if is_active:
            query = query.filter(MapTopic.is_active == True)
        query = query.order_by(desc(MapTopic.check_in_count), desc(MapTopic.created_at))
        total = query.count()
        topics = query.offset(skip).limit(limit).all()
        return topics, total

    @staticmethod
    def get_hot_topics(db: Session, limit: int = 10) -> List[MapTopic]:
        return (
            db.query(MapTopic)
            .filter(MapTopic.is_active == True)
            .order_by(desc(MapTopic.check_in_count))
            .limit(limit)
            .all()
        )


class MapStatsService:
    """地图统计服务"""

    @staticmethod
    def get_stats(db: Session) -> dict:
        total_pois = db.query(POI).filter(POI.status == "approved").count()
        total_check_ins = db.query(CheckIn).filter(CheckIn.is_active == True).count()
        total_users = db.query(User).filter(User.is_active == True).count()
        total_topics = db.query(MapTopic).filter(MapTopic.is_active == True).count()
        hot_pois = POIService.get_hot_pois(db, limit=5)
        hot_topics = TopicService.get_hot_topics(db, limit=5)
        recent_check_ins = CheckInService.get_recent_check_ins(db, limit=10)

        return {
            "total_pois": total_pois,
            "total_check_ins": total_check_ins,
            "total_users": total_users,
            "total_topics": total_topics,
            "hot_pois": hot_pois,
            "hot_topics": hot_topics,
            "recent_check_ins": recent_check_ins
        }
