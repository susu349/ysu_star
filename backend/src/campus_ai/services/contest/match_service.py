"""
赛事匹配服务 - 个性化推荐与队友匹配
"""
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ...models import (
    Contest, Team, TeamMember, UserContestTag,
    ContestLevel, ContestStatus, TeamStatus
)


class ContestMatchService:
    """赛事推荐匹配服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_tags(self, user_id: str) -> Dict[str, int]:
        """获取用户标签及其权重"""
        tags = self.db.query(UserContestTag).filter(
            UserContestTag.user_id == user_id
        ).all()
        return {tag.tag: tag.weight for tag in tags}

    def add_user_tag(self, user_id: str, tag: str, weight: int = 1) -> None:
        """添加用户标签"""
        existing = self.db.query(UserContestTag).filter(
            UserContestTag.user_id == user_id,
            UserContestTag.tag == tag
        ).first()

        if existing:
            existing.weight += weight
        else:
            user_tag = UserContestTag(
                id=str(uuid.uuid4()),
                user_id=user_id,
                tag=tag,
                weight=weight
            )
            self.db.add(user_tag)

        self.db.commit()

    def calculate_contest_score(
        self,
        contest: Contest,
        user_tags: Dict[str, int]
    ) -> float:
        """计算赛事与用户的匹配分数"""
        score = 0.0

        # 标签匹配
        contest_tags = set(contest.tags or [])
        for tag, weight in user_tags.items():
            if tag in contest_tags:
                score += weight * 10

        # 分类匹配
        if contest.category:
            category_match = user_tags.get(contest.category, 0)
            score += category_match * 5

        # 级别偏好（假设用户有级别标签）
        level_tags = {
            ContestLevel.SCHOOL: "校赛",
            ContestLevel.PROVINCE: "省赛",
            ContestLevel.NATIONAL: "国赛",
            ContestLevel.INTERNATIONAL: "国际赛",
        }
        if contest.level in level_tags:
            level_score = user_tags.get(level_tags[contest.level], 0)
            score += level_score * 3

        # 时间因素 - 即将截止的加分
        if contest.registration_end:
            from datetime import datetime, timedelta
            days_left = (contest.registration_end - datetime.utcnow()).days
            if 0 <= days_left <= 7:
                score += 20  # 紧急截止
            elif 7 < days_left <= 30:
                score += 10  # 即将截止

        # 热门程度
        if contest.view_count:
            score += min(contest.view_count / 100, 10)

        return score

    def recommend_contests(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[Contest]:
        """为用户推荐赛事"""
        user_tags = self.get_user_tags(user_id)

        # 获取可报名的赛事
        contests = self.db.query(Contest).filter(
            Contest.status.in_([
                ContestStatus.PUBLISHED,
                ContestStatus.REGISTRATION_OPEN
            ])
        ).all()

        # 计算分数并排序
        scored = []
        for contest in contests:
            score = self.calculate_contest_score(contest, user_tags)
            scored.append((score, contest))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [contest for _, contest in scored[:limit]]


class TeamMatchService:
    """队友匹配服务"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_team_match_score(
        self,
        team: Team,
        user_skills: List[str],
        user_tags: Dict[str, int]
    ) -> float:
        """计算用户与队伍的匹配分数"""
        score = 0.0

        # 技能匹配
        required_skills = set(team.required_skills or [])
        user_skill_set = set(user_skills)

        matched_skills = required_skills & user_skill_set
        score += len(matched_skills) * 15

        # 缺失技能（稀缺技能加分）
        missing_skills = required_skills - user_skill_set
        if not missing_skills:
            score += 20  # 完全满足技能需求

        # 标签匹配
        team_name = team.name or ""
        team_desc = team.description or ""
        for tag, weight in user_tags.items():
            if tag in team_name or tag in team_desc:
                score += weight * 5

        # 队伍规模偏好（接近满员但还没满的加分）
        current_size = len(team.members) if team.members else 0
        max_size = team.max_members or 5
        spots_left = max_size - current_size

        if spots_left == 1:
            score += 5  # 最后一个名额
        elif spots_left == 0:
            score -= 100  # 已满员，不推荐

        return score

    def recommend_teams_for_user(
        self,
        user_id: str,
        contest_id: Optional[str] = None,
        user_skills: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Team]:
        """为用户推荐合适的队伍"""
        from .storage_service import ContestStorageService

        contest_storage = ContestStorageService(self.db)
        match_service = ContestMatchService(self.db)

        user_tags = match_service.get_user_tags(user_id)
        user_skills = user_skills or []

        # 查询招募中的队伍
        query = self.db.query(Team).filter(Team.status == TeamStatus.RECRUITING)

        if contest_id:
            query = query.filter(Team.contest_id == contest_id)

        teams = query.all()

        # 计算匹配分数
        scored = []
        for team in teams:
            score = self.calculate_team_match_score(team, user_skills, user_tags)
            scored.append((score, team))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [team for _, team in scored[:limit]]

    def find_similar_users_for_team(
        self,
        team: Team,
        limit: int = 10,
    ) -> List[str]:
        """为队伍寻找合适的用户（返回用户ID列表）"""
        # 获取队伍需要的技能
        required_skills = set(team.required_skills or [])
        if not required_skills:
            return []

        # 查找有相关标签的用户
        user_tags = self.db.query(UserContestTag).filter(
            UserContestTag.tag.in_(required_skills)
        ).all()

        # 统计用户匹配度
        user_scores: Dict[str, int] = {}
        for ut in user_tags:
            user_scores[ut.user_id] = user_scores.get(ut.user_id, 0) + ut.weight

        # 排序并返回
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        return [user_id for user_id, _ in sorted_users[:limit]]
