"""
队伍管理服务 - 组队、申请、任务管理
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...models import (
    Team, TeamMember, TeamApplication,
    TeamStatus, TeamMemberRole, ApplicationStatus
)
from .storage_service import TeamStorageService


class TeamService:
    """队伍管理服务"""

    def __init__(self, db: Session):
        self.db = db
        self.storage = TeamStorageService(db)

    def is_user_in_team(self, team_id: str, user_id: str) -> bool:
        """检查用户是否在队伍中"""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        return member is not None

    def is_user_team_leader(self, team_id: str, user_id: str) -> bool:
        """检查用户是否是队长"""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.role == TeamMemberRole.LEADER
        ).first()
        return member is not None

    def get_team_members(self, team_id: str) -> List[TeamMember]:
        """获取队伍成员"""
        return self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()

    def apply_to_join_team(
        self,
        team_id: str,
        user_id: str,
        message: Optional[str] = None,
    ) -> TeamApplication:
        """申请加入队伍"""
        # 检查是否已经在队伍中
        if self.is_user_in_team(team_id, user_id):
            raise ValueError("您已经在该队伍中")

        # 检查是否已有待处理的申请
        existing = self.db.query(TeamApplication).filter(
            TeamApplication.team_id == team_id,
            TeamApplication.applicant_id == user_id,
            TeamApplication.status == ApplicationStatus.PENDING
        ).first()

        if existing:
            raise ValueError("您已有待处理的申请")

        application = TeamApplication(
            id=str(uuid.uuid4()),
            team_id=team_id,
            applicant_id=user_id,
            message=message,
            status=ApplicationStatus.PENDING,
        )

        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def handle_application(
        self,
        application_id: str,
        handler_id: str,
        approved: bool,
        handled_message: Optional[str] = None,
    ) -> Optional[TeamApplication]:
        """处理入队申请"""
        application = self.db.query(TeamApplication).filter(
            TeamApplication.id == application_id
        ).first()

        if not application:
            return None

        if application.status != ApplicationStatus.PENDING:
            raise ValueError("申请已被处理")

        # 验证处理者是队长
        if not self.is_user_team_leader(application.team_id, handler_id):
            raise ValueError("只有队长可以处理申请")

        application.status = ApplicationStatus.APPROVED if approved else ApplicationStatus.REJECTED
        application.handled_by = handler_id
        application.handled_at = datetime.utcnow()
        application.handled_message = handled_message

        if approved:
            # 加入队伍
            team = self.storage.get_team_by_id(application.team_id)
            if team:
                # 检查队伍是否已满
                members = self.get_team_members(team.id)
                if len(members) >= team.max_members:
                    team.status = TeamStatus.FULL
                    raise ValueError("队伍已满")

                # 添加成员
                member = TeamMember(
                    id=str(uuid.uuid4()),
                    team_id=application.team_id,
                    user_id=application.applicant_id,
                    role=TeamMemberRole.MEMBER,
                )
                self.db.add(member)

                # 检查是否满员
                members_after = self.get_team_members(team.id)
                if len(members_after) >= team.max_members:
                    team.status = TeamStatus.FULL

        self.db.commit()
        self.db.refresh(application)
        return application

    def leave_team(self, team_id: str, user_id: str) -> bool:
        """退出队伍"""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if not member:
            return False

        # 队长不能直接退出，需要先转让队长或解散队伍
        if member.role == TeamMemberRole.LEADER:
            # 检查是否有其他成员可以转让
            other_members = self.db.query(TeamMember).filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id != user_id
            ).first()

            if other_members:
                raise ValueError("请先转让队长给其他成员")
            else:
                # 没有其他成员，解散队伍
                team = self.storage.get_team_by_id(team_id)
                if team:
                    team.status = TeamStatus.DISBANDED

        # 移除成员
        self.db.delete(member)

        # 更新队伍状态
        team = self.storage.get_team_by_id(team_id)
        if team and team.status == TeamStatus.FULL:
            team.status = TeamStatus.RECRUITING

        self.db.commit()
        return True

    def remove_team_member(
        self,
        team_id: str,
        target_user_id: str,
        operator_id: str,
    ) -> bool:
        """移除队员（队长权限）"""
        if not self.is_user_team_leader(team_id, operator_id):
            raise ValueError("只有队长可以移除队员")

        if target_user_id == operator_id:
            raise ValueError("不能移除自己，请使用退出队伍功能")

        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == target_user_id
        ).first()

        if not member:
            return False

        self.db.delete(member)

        # 更新队伍状态
        team = self.storage.get_team_by_id(team_id)
        if team and team.status == TeamStatus.FULL:
            team.status = TeamStatus.RECRUITING

        self.db.commit()
        return True

    def transfer_leadership(
        self,
        team_id: str,
        new_leader_id: str,
        current_leader_id: str,
    ) -> bool:
        """转让队长"""
        if not self.is_user_team_leader(team_id, current_leader_id):
            raise ValueError("只有队长可以转让权限")

        # 获取当前队长
        current_leader = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_leader_id
        ).first()

        # 获取新队长
        new_leader = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == new_leader_id
        ).first()

        if not new_leader:
            raise ValueError("新队长不在队伍中")

        current_leader.role = TeamMemberRole.MEMBER
        new_leader.role = TeamMemberRole.LEADER

        self.db.commit()
        return True

    def get_pending_applications(self, team_id: str) -> List[TeamApplication]:
        """获取待处理的申请"""
        return self.db.query(TeamApplication).filter(
            TeamApplication.team_id == team_id,
            TeamApplication.status == ApplicationStatus.PENDING
        ).all()

    def get_user_applications(self, user_id: str) -> List[TeamApplication]:
        """获取用户的申请记录"""
        return self.db.query(TeamApplication).filter(
            TeamApplication.applicant_id == user_id
        ).order_by(TeamApplication.created_at.desc()).all()

    def add_team_task(
        self,
        team_id: str,
        task_title: str,
        task_description: Optional[str] = None,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> Optional[Team]:
        """添加队伍任务"""
        team = self.storage.get_team_by_id(team_id)
        if not team:
            return None

        task = {
            "id": str(uuid.uuid4()),
            "title": task_title,
            "description": task_description,
            "assigned_to": assigned_to,
            "due_date": due_date.isoformat() if due_date else None,
            "completed": False,
            "created_at": datetime.utcnow().isoformat(),
        }

        tasks = team.tasks or []
        tasks.append(task)
        team.tasks = tasks

        self.db.commit()
        self.db.refresh(team)
        return team

    def update_team_task(
        self,
        team_id: str,
        task_id: str,
        completed: Optional[bool] = None,
        **kwargs,
    ) -> Optional[Team]:
        """更新队伍任务"""
        team = self.storage.get_team_by_id(team_id)
        if not team or not team.tasks:
            return None

        tasks = team.tasks
        for task in tasks:
            if task.get("id") == task_id:
                if completed is not None:
                    task["completed"] = completed
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                break

        team.tasks = tasks
        self.db.commit()
        self.db.refresh(team)
        return team
