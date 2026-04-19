"""
赛事模块 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ...core.security import get_current_active_user
from ...models import User
from ...models.contest import (
    ContestLevel, ContestStatus, TeamStatus, ApplicationStatus
)
from ...schemas.contest import (
    ContestCreate, ContestUpdate, ContestResponse, ContestListResponse,
    TeamCreate, TeamUpdate, TeamResponse, TeamListResponse,
    TeamApplicationCreate, TeamApplicationHandle, TeamApplicationResponse,
    TeamTaskCreate, TeamTaskUpdate,
    UserContestTagCreate,
    CrawlRequest,
    ContestRecommendRequest,
    ContestCommentCreate, ContestCommentUpdate, ContestCommentResponse, ContestCommentListResponse,
    PrivateMessageCreate, PrivateMessageResponse, PrivateMessageListResponse, PrivateConversationResponse,
)
from ...services.contest import (
    ContestStorageService, TeamStorageService,
    ContestMatchService, TeamMatchService,
    TeamService,
    YsuContestCrawler,
    ContestAIProcessor,
    init_static_contest_data, init_static_team_data,
)

router = APIRouter(prefix="/contest", tags=["赛事"])


# ============== 赛事管理 ==============

@router.get("/list", response_model=ContestListResponse)
def list_contests(
    status: Optional[ContestStatus] = None,
    level: Optional[ContestLevel] = None,
    category: Optional[str] = None,
    search: Optional[str] = Query(None, description="按名称搜索"),
    order_by: Optional[str] = Query("created_at", description="排序字段: created_at, registration_end, title"),
    order_dir: Optional[str] = Query("desc", description="排序方向: asc, desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """获取赛事列表"""
    storage = ContestStorageService(db)
    contests = storage.list_contests(
        status=status, level=level, category=category,
        search=search, order_by=order_by, order_dir=order_dir,
        skip=skip, limit=limit
    )
    total = len(contests)  # 简化版，实际应该 count
    return ContestListResponse(total=total, items=contests)


@router.get("/{contest_id}", response_model=ContestResponse)
def get_contest(
    contest_id: str,
    db: Session = Depends(get_db),
):
    """获取赛事详情"""
    storage = ContestStorageService(db)
    contest = storage.get_contest_by_id(contest_id)
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="赛事不存在"
        )
    storage.increment_view_count(contest_id)
    return contest


@router.post("/", response_model=ContestResponse, status_code=status.HTTP_201_CREATED)
def create_contest(
    contest_data: ContestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建赛事（管理员）"""
    # TODO: 检查权限
    storage = ContestStorageService(db)
    return storage.create_contest(**contest_data.model_dump())


@router.put("/{contest_id}", response_model=ContestResponse)
def update_contest(
    contest_id: str,
    contest_data: ContestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新赛事"""
    storage = ContestStorageService(db)
    contest = storage.update_contest(contest_id, **contest_data.model_dump(exclude_unset=True))
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="赛事不存在"
        )
    return contest


# ============== 赛事推荐 ==============

@router.get("/recommend/my", response_model=List[ContestResponse])
def get_recommended_contests(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取为我推荐的赛事"""
    match_service = ContestMatchService(db)
    return match_service.recommend_contests(current_user.id, limit=limit)


@router.post("/tags", status_code=status.HTTP_200_OK)
def add_user_tag(
    tag_data: UserContestTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """添加用户标签"""
    match_service = ContestMatchService(db)
    match_service.add_user_tag(current_user.id, tag_data.tag, tag_data.weight)
    return {"message": "标签添加成功"}


# ============== 队伍管理 ==============

@router.get("/{contest_id}/teams", response_model=TeamListResponse)
def list_contest_teams(
    contest_id: str,
    status: Optional[TeamStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取某赛事的队伍列表"""
    storage = TeamStorageService(db)
    teams = storage.list_teams_by_contest(
        contest_id, status=status, skip=skip, limit=limit
    )
    return TeamListResponse(total=len(teams), items=teams)


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
):
    """获取队伍详情"""
    storage = TeamStorageService(db)
    team = storage.get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="队伍不存在"
        )
    return team


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建队伍"""
    team_service = TeamService(db)
    if team_service.is_user_in_team(team_data.contest_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已在该赛事中有队伍"
        )

    storage = TeamStorageService(db)
    return storage.create_team(
        contest_id=team_data.contest_id,
        user_id=current_user.id,
        **team_data.model_dump(exclude={"contest_id"})
    )


@router.put("/teams/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新队伍（队长）"""
    team_service = TeamService(db)
    if not team_service.is_user_team_leader(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有队长可以修改队伍信息"
        )

    storage = TeamStorageService(db)
    team = storage.update_team(team_id, **team_data.model_dump(exclude_unset=True))
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="队伍不存在"
        )
    return team


@router.post("/teams/recommend", response_model=List[TeamResponse])
def recommend_teams(
    contest_id: Optional[str] = None,
    user_skills: Optional[List[str]] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """推荐合适的队伍"""
    match_service = TeamMatchService(db)
    return match_service.recommend_teams_for_user(
        current_user.id, contest_id=contest_id,
        user_skills=user_skills, limit=limit
    )


# ============== 组队申请 ==============

@router.post("/teams/{team_id}/apply", response_model=TeamApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_team(
    team_id: str,
    application_data: Optional[TeamApplicationCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """申请加入队伍"""
    team_service = TeamService(db)
    try:
        return team_service.apply_to_join_team(
            team_id, current_user.id,
            application_data.message if application_data else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/teams/{team_id}/applications", response_model=List[TeamApplicationResponse])
def get_pending_applications(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取待处理的申请（队长）"""
    team_service = TeamService(db)
    if not team_service.is_user_team_leader(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有队长可以查看申请"
        )
    return team_service.get_pending_applications(team_id)


@router.get("/my/applications", response_model=List[TeamApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取我的申请记录"""
    team_service = TeamService(db)
    return team_service.get_user_applications(current_user.id)


@router.post("/applications/{application_id}/handle", response_model=TeamApplicationResponse)
def handle_application(
    application_id: str,
    handle_data: TeamApplicationHandle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """处理入队申请（队长）"""
    team_service = TeamService(db)
    try:
        application = team_service.handle_application(
            application_id, current_user.id,
            handle_data.approved, handle_data.handled_message
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在"
            )
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============== 队伍成员管理 ==============

@router.post("/teams/{team_id}/leave", status_code=status.HTTP_200_OK)
def leave_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """退出队伍"""
    team_service = TeamService(db)
    try:
        success = team_service.leave_team(team_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="您不在该队伍中"
            )
        return {"message": "已退出队伍"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/teams/{team_id}/members/{member_id}", status_code=status.HTTP_200_OK)
def remove_team_member(
    team_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """移除队员（队长）"""
    team_service = TeamService(db)
    try:
        success = team_service.remove_team_member(team_id, member_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="成员不存在"
            )
        return {"message": "已移除成员"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============== 队伍任务管理 ==============

@router.post("/teams/{team_id}/tasks", response_model=TeamResponse)
def add_team_task(
    team_id: str,
    task_data: TeamTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """添加队伍任务（队长）"""
    team_service = TeamService(db)
    if not team_service.is_user_team_leader(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有队长可以添加任务"
        )

    team = team_service.add_team_task(team_id, **task_data.model_dump())
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="队伍不存在"
        )
    return team


@router.put("/teams/{team_id}/tasks/{task_id}", response_model=TeamResponse)
def update_team_task(
    team_id: str,
    task_id: str,
    task_data: TeamTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新队伍任务"""
    team_service = TeamService(db)
    if not team_service.is_user_in_team(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不在该队伍中"
        )

    team = team_service.update_team_task(team_id, task_id, **task_data.model_dump(exclude_unset=True))
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="队伍或任务不存在"
        )
    return team


# ============== 爬虫与数据初始化 ==============

@router.post("/crawl", status_code=status.HTTP_200_OK)
def crawl_contests(
    crawl_data: CrawlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """爬取赛事（管理员）"""
    # TODO: 检查权限
    crawler = YsuContestCrawler(db)
    try:
        contests = crawler.run_full_crawl(max_pages=crawl_data.max_pages)
        return {
            "message": f"成功爬取 {len(contests)} 个赛事",
            "contest_ids": [c.id for c in contests]
        }
    finally:
        crawler.close()


@router.post("/process/{contest_id}", response_model=ContestResponse)
def process_contest(
    contest_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI处理赛事信息"""
    processor = ContestAIProcessor(db)
    contest = processor.process_contest(contest_id)
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="赛事不存在"
        )
    return contest


@router.post("/init-static", status_code=status.HTTP_200_OK)
def init_static_data(
    db: Session = Depends(get_db),
):
    """初始化静态假数据"""
    init_static_contest_data(db)
    init_static_team_data(db, "static_user_1")
    return {"message": "静态数据初始化完成"}


# ============== 评论管理 ==============

@router.get("/{contest_id}/comments", response_model=ContestCommentListResponse)
def list_contest_comments(
    contest_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取赛事评论列表"""
    from ...models.contest import ContestComment

    query = db.query(ContestComment).filter(
        ContestComment.contest_id == contest_id,
        ContestComment.is_deleted == False,
        ContestComment.parent_id == None
    )

    total = query.count()
    comments = query.order_by(
        ContestComment.is_pinned.desc(),
        ContestComment.created_at.desc()
    ).offset(skip).limit(limit).all()

    return ContestCommentListResponse(total=total, items=comments)


@router.post("/comments", response_model=ContestCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: ContestCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建评论"""
    from ...models.contest import ContestComment
    import uuid

    comment = ContestComment(
        id=str(uuid.uuid4()),
        contest_id=comment_data.contest_id,
        user_id=current_user.id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.put("/comments/{comment_id}", response_model=ContestCommentResponse)
def update_comment(
    comment_id: str,
    comment_data: ContestCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新评论"""
    from ...models.contest import ContestComment

    comment = db.query(ContestComment).filter(
        ContestComment.id == comment_id,
        ContestComment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的评论"
        )

    if comment_data.content:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除评论"""
    from ...models.contest import ContestComment

    comment = db.query(ContestComment).filter(
        ContestComment.id == comment_id,
        ContestComment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的评论"
        )

    comment.is_deleted = True
    db.commit()
    return {"message": "评论已删除"}


@router.post("/comments/{comment_id}/like", status_code=status.HTTP_200_OK)
def like_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """点赞评论"""
    from ...models.contest import ContestComment

    comment = db.query(ContestComment).filter(
        ContestComment.id == comment_id,
        ContestComment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    comment.like_count = (comment.like_count or 0) + 1
    db.commit()
    return {"message": "点赞成功", "like_count": comment.like_count}


# ============== 私信管理 ==============

@router.get("/messages/conversations", response_model=List[PrivateConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取会话列表"""
    from ...models.contest import PrivateMessage
    from sqlalchemy import or_, and_, func

    # 获取所有与当前用户相关的消息
    subquery = db.query(
        func.max(PrivateMessage.created_at).label('last_created'),
        func.case(
            (PrivateMessage.sender_id == current_user.id, PrivateMessage.receiver_id),
            else_=PrivateMessage.sender_id
        ).label('other_user_id')
    ).filter(
        or_(
            PrivateMessage.sender_id == current_user.id,
            PrivateMessage.receiver_id == current_user.id
        ),
        and_(
            or_(
                PrivateMessage.sender_id == current_user.id,
                PrivateMessage.is_deleted_by_receiver == False
            ),
            or_(
                PrivateMessage.receiver_id == current_user.id,
                PrivateMessage.is_deleted_by_sender == False
            )
        )
    ).group_by(
        func.case(
            (PrivateMessage.sender_id == current_user.id, PrivateMessage.receiver_id),
            else_=PrivateMessage.sender_id
        )
    ).subquery()

    # 获取每个会话的最后一条消息
    conversations = []
    results = db.query(subquery).all()

    for row in results:
        other_user_id = row.other_user_id
        last_created = row.last_created

        # 获取最后一条消息
        last_msg = db.query(PrivateMessage).filter(
            or_(
                and_(
                    PrivateMessage.sender_id == current_user.id,
                    PrivateMessage.receiver_id == other_user_id
                ),
                and_(
                    PrivateMessage.sender_id == other_user_id,
                    PrivateMessage.receiver_id == current_user.id
                )
            ),
            PrivateMessage.created_at == last_created
        ).first()

        # 获取未读消息数
        unread_count = db.query(PrivateMessage).filter(
            PrivateMessage.sender_id == other_user_id,
            PrivateMessage.receiver_id == current_user.id,
            PrivateMessage.is_read == False,
            PrivateMessage.is_deleted_by_receiver == False
        ).count()

        conversations.append(PrivateConversationResponse(
            user_id=other_user_id,
            last_message=last_msg,
            unread_count=unread_count
        ))

    # 按最后消息时间排序
    conversations.sort(key=lambda x: x.last_message.created_at if x.last_message else None, reverse=True)
    return conversations


@router.get("/messages/{user_id}", response_model=PrivateMessageListResponse)
def get_messages_with_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取与某用户的聊天记录"""
    from ...models.contest import PrivateMessage
    from sqlalchemy import or_, and_

    query = db.query(PrivateMessage).filter(
        or_(
            and_(
                PrivateMessage.sender_id == current_user.id,
                PrivateMessage.receiver_id == user_id,
                PrivateMessage.is_deleted_by_sender == False
            ),
            and_(
                PrivateMessage.sender_id == user_id,
                PrivateMessage.receiver_id == current_user.id,
                PrivateMessage.is_deleted_by_receiver == False
            )
        )
    )

    total = query.count()
    messages = query.order_by(PrivateMessage.created_at.desc()).offset(skip).limit(limit).all()

    # 标记为已读
    unread_messages = db.query(PrivateMessage).filter(
        PrivateMessage.sender_id == user_id,
        PrivateMessage.receiver_id == current_user.id,
        PrivateMessage.is_read == False
    ).all()

    for msg in unread_messages:
        msg.is_read = True

    db.commit()

    return PrivateMessageListResponse(total=total, items=list(reversed(messages)))


@router.post("/messages", response_model=PrivateMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: PrivateMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """发送私信"""
    from ...models.contest import PrivateMessage
    import uuid

    if message_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能给自己发消息"
        )

    message = PrivateMessage(
        id=str(uuid.uuid4()),
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除私信"""
    from ...models.contest import PrivateMessage

    message = db.query(PrivateMessage).filter(
        PrivateMessage.id == message_id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此消息"
        )

    if message.sender_id == current_user.id:
        message.is_deleted_by_sender = True
    if message.receiver_id == current_user.id:
        message.is_deleted_by_receiver = True

    db.commit()
    return {"message": "消息已删除"}
