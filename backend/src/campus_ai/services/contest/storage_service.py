"""
赛事存储服务 - 包括静态假数据初始化
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from ...models import (
    Contest, Team, TeamMember, TeamApplication,
    ContestLevel, ContestStatus, TeamStatus, TeamMemberRole, ApplicationStatus
)
from ...core.database import SessionLocal


class ContestStorageService:
    """赛事存储服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_contest_by_id(self, contest_id: str) -> Optional[Contest]:
        """根据ID获取赛事"""
        return self.db.query(Contest).filter(Contest.id == contest_id).first()

    def list_contests(
        self,
        status: Optional[ContestStatus] = None,
        level: Optional[ContestLevel] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_dir: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> List[Contest]:
        """获取赛事列表"""
        from sqlalchemy import or_, func, case

        query = self.db.query(Contest)

        if status:
            query = query.filter(Contest.status == status)
        if level:
            query = query.filter(Contest.level == level)
        if category:
            query = query.filter(Contest.category == category)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Contest.title.ilike(search_term),
                    Contest.summary.ilike(search_term),
                    Contest.organizer.ilike(search_term)
                )
            )

        # 排序
        if order_by == "source_url":
            # 从 source_url 中提取最后一个数字进行排序
            # 例如: https://cxcy.ysu.edu.cn/info/1043/3162.htm -> 3162
            from sqlalchemy.ext.compiler import compiles
            from sqlalchemy.sql.expression import FunctionElement

            # 使用正则提取 URL 末尾的数字
            url_number = func.cast(
                func.substring(
                    Contest.source_url,
                    func.char_length(Contest.source_url) - func.position(
                        func.reverse('.htm'), func.reverse(Contest.source_url)
                    ) - func.position(
                        '/', func.reverse(Contest.source_url), func.position(
                            '/', func.reverse(Contest.source_url)
                        ) + 1
                    ) + 2,
                    func.position(
                        '/', func.reverse(Contest.source_url), func.position(
                            '/', func.reverse(Contest.source_url)
                        ) + 1
                    ) - func.position(
                        func.reverse('.htm'), func.reverse(Contest.source_url)
                    ) - 1
                ),
                func.Integer
            )

            # 简化方案：按 created_at 排序作为默认，或者先获取所有数据在 Python 中排序
            # 这里先查询所有数据，然后在 Python 中处理排序
            all_contests = query.all()

            def get_url_number(contest):
                if not contest.source_url:
                    return 0
                try:
                    # 从 URL 中提取最后一个数字部分
                    # 格式: /info/1043/3162.htm -> 提取 3162
                    parts = contest.source_url.rstrip('.htm').rstrip('.html').split('/')
                    for part in reversed(parts):
                        if part and part.isdigit():
                            return int(part)
                    return 0
                except:
                    return 0

            all_contests.sort(key=get_url_number, reverse=(order_dir == "desc"))
            return all_contests[skip:skip+limit] if limit > 0 else all_contests[skip:]
        else:
            order_column = getattr(Contest, order_by, Contest.created_at)
            if order_dir == "asc":
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())

            return query.offset(skip).limit(limit).all()

    def create_contest(self, **kwargs) -> Contest:
        """创建赛事"""
        contest = Contest(
            id=str(uuid.uuid4()),
            **kwargs
        )
        self.db.add(contest)
        self.db.commit()
        self.db.refresh(contest)
        return contest

    def update_contest(self, contest_id: str, **kwargs) -> Optional[Contest]:
        """更新赛事"""
        contest = self.get_contest_by_id(contest_id)
        if not contest:
            return None

        for key, value in kwargs.items():
            if hasattr(contest, key):
                setattr(contest, key, value)

        self.db.commit()
        self.db.refresh(contest)
        return contest

    def increment_view_count(self, contest_id: str) -> None:
        """增加浏览次数"""
        contest = self.get_contest_by_id(contest_id)
        if contest:
            contest.view_count = (contest.view_count or 0) + 1
            self.db.commit()


class TeamStorageService:
    """队伍存储服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """根据ID获取队伍"""
        return self.db.query(Team).filter(Team.id == team_id).first()

    def list_teams_by_contest(
        self,
        contest_id: str,
        status: Optional[TeamStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Team]:
        """获取某赛事的队伍列表"""
        query = self.db.query(Team).filter(Team.contest_id == contest_id)

        if status:
            query = query.filter(Team.status == status)

        return query.order_by(Team.created_at.desc()).offset(skip).limit(limit).all()

    def create_team(self, contest_id: str, user_id: str, **kwargs) -> Team:
        """创建队伍（创建者自动成为队长）"""
        team = Team(
            id=str(uuid.uuid4()),
            contest_id=contest_id,
            status=TeamStatus.RECRUITING,
            **kwargs
        )
        self.db.add(team)
        self.db.flush()

        # 添加创建者为队长
        member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=team.id,
            user_id=user_id,
            role=TeamMemberRole.LEADER,
        )
        self.db.add(member)

        # 更新赛事组队数量
        contest = self.db.query(Contest).filter(Contest.id == contest_id).first()
        if contest:
            contest.team_count = (contest.team_count or 0) + 1

        self.db.commit()
        self.db.refresh(team)
        return team

    def update_team(self, team_id: str, **kwargs) -> Optional[Team]:
        """更新队伍信息"""
        team = self.get_team_by_id(team_id)
        if not team:
            return None

        for key, value in kwargs.items():
            if hasattr(team, key):
                setattr(team, key, value)

        self.db.commit()
        self.db.refresh(team)
        return team


def init_static_contest_data(db: Session) -> None:
    """初始化静态假数据"""
    # 检查是否已有数据
    existing = db.query(Contest).first()
    if existing:
        print("已有赛事数据，跳过初始化")
        return

    now = datetime.utcnow()

    # 静态假数据
    contests_data = [
        {
            "title": "第十五届'挑战杯'河北省大学生课外学术科技作品竞赛",
            "summary": "河北省大学生顶级科技竞赛，校赛选拔已启动，欢迎各学院同学组队参加！",
            "description": """
竞赛主题：崇尚科学、追求真知、勤奋学习、锐意创新、迎接挑战
参赛对象：全日制在校本科生、研究生
赛事级别：省级
报名截止：2024年5月30日
            """,
            "level": ContestLevel.PROVINCE,
            "category": "科技创新",
            "tags": ["挑战杯", "科技作品", "课外学术"],
            "status": ContestStatus.REGISTRATION_OPEN,
            "registration_end": now + timedelta(days=30),
            "contest_start": now + timedelta(days=60),
            "organizer": "共青团河北省委、河北省教育厅",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": "2024年'互联网+'大学生创新创业大赛校赛",
            "summary": "中国国际'互联网+'大学生创新创业大赛燕山大学校内选拔赛开始报名！",
            "description": """
参赛组别：高教主赛道、青年红色筑梦之旅赛道、职教赛道
参赛项目类型：
- 现代农业
- 制造业
- 信息技术服务
- 文化创意服务
- 社会服务

校级金奖项目将推荐参加省赛！
            """,
            "level": ContestLevel.SCHOOL,
            "category": "创新创业",
            "tags": ["互联网+", "创新创业", "校赛"],
            "status": ContestStatus.REGISTRATION_OPEN,
            "registration_end": now + timedelta(days=45),
            "contest_start": now + timedelta(days=75),
            "organizer": "燕山大学创新创业学院",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": "全国大学生数学建模竞赛",
            "summary": "2024年全国大学生数学建模竞赛报名通知，3人组队，三天三夜挑战！",
            "description": """
竞赛时间：2024年9月（具体待定）
参赛对象：全日制在校本科生
组队要求：3人组队，专业不限，鼓励跨学科组队
竞赛内容：A/B/C/D四题选做其一，提交论文

学校将组织赛前培训！
            """,
            "level": ContestLevel.NATIONAL,
            "category": "数学建模",
            "tags": ["数学建模", "国赛", "论文"],
            "status": ContestStatus.PUBLISHED,
            "registration_start": now + timedelta(days=60),
            "registration_end": now + timedelta(days=90),
            "contest_start": now + timedelta(days=120),
            "organizer": "全国大学生数学建模竞赛组委会",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": "ACM-ICPC程序设计竞赛校队选拔赛",
            "summary": "选拔优秀选手代表学校参加ACM-ICPC国际大学生程序设计竞赛！",
            "description": """
参赛对象：全体在校本科生
选拔方式：
- 选拔赛1：4月
- 选拔赛2：5月
- 最终集训队名单6月公布

比赛形式：3人组队，现场编程，5小时解决8-10题

奖项设置：
- 一等奖1队
- 二等奖2队
- 三等奖3队
            """,
            "level": ContestLevel.SCHOOL,
            "category": "程序设计",
            "tags": ["ACM", "程序设计", "算法"],
            "status": ContestStatus.REGISTRATION_OPEN,
            "registration_end": now + timedelta(days=10),
            "contest_start": now + timedelta(days=15),
            "organizer": "燕山大学信息科学与工程学院",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": "大学生电子设计竞赛",
            "summary": "2024年全国大学生电子设计竞赛燕山大学报名通知！",
            "description": """
竞赛时间：2024年8月（两年一届）
参赛对象：全日制在校本科生
组队要求：3人组队

竞赛题目：
- 自动控制类
- 电力电子类
- 通信类
- 仪器仪表类

学校提供实验室和设备支持！
            """,
            "level": ContestLevel.NATIONAL,
            "category": "电子设计",
            "tags": ["电子设计", "嵌入式", "硬件"],
            "status": ContestStatus.PUBLISHED,
            "registration_start": now + timedelta(days=90),
            "registration_end": now + timedelta(days=120),
            "contest_start": now + timedelta(days=150),
            "organizer": "全国大学生电子设计竞赛组委会",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": '中国大学生计算机设计大赛',
            "summary": "2024年中国大学生计算机设计大赛作品征集开始！",
            "description": """
参赛类别：
- 软件应用与开发
- 微课与教学辅助
- 数字媒体设计
- 人工智能
- 大数据应用

参赛对象：全日制在校本科生
作品提交截止：2024年5月20日
            """,
            "level": ContestLevel.NATIONAL,
            "category": "计算机设计",
            "tags": ["计设赛", "软件设计", "数字媒体"],
            "status": ContestStatus.REGISTRATION_OPEN,
            "registration_end": now + timedelta(days=25),
            "contest_start": now + timedelta(days=50),
            "organizer": "中国大学生计算机设计大赛组委会",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": "机械创新设计大赛",
            "summary": "第十届全国大学生机械创新设计大赛校赛通知！",
            "description": """
竞赛主题：
- 面向乡村振兴的机械设计
- 面向制造业高质量发展的机械设计

参赛对象：机械类及相关专业本科生
赛事级别：国家级
            """,
            "level": ContestLevel.NATIONAL,
            "category": "机械设计",
            "tags": ["机械创新", "结构设计", "三维建模"],
            "status": ContestStatus.PUBLISHED,
            "registration_start": now + timedelta(days=180),
            "contest_start": now + timedelta(days=240),
            "organizer": "全国大学生机械创新设计大赛组委会",
            "is_ai_processed": True,
            "source": "manual",
        },
        {
            "title": '节能减排社会实践与科技竞赛',
            "summary": "全国大学生节能减排社会实践与科技竞赛作品征集！",
            "description": """
竞赛主题：节能减排、绿色能源
参赛形式：
- 科技作品类
- 社会实践调查报告类
- 科技发明制作类

赛事级别：国家级
            """,
            "level": ContestLevel.NATIONAL,
            "category": "节能减排",
            "tags": ["节能减排", "绿色能源", "环保"],
            "status": ContestStatus.PUBLISHED,
            "registration_start": now + timedelta(days=150),
            "contest_start": now + timedelta(days=200),
            "organizer": "全国大学生节能减排竞赛组委会",
            "is_ai_processed": True,
            "source": "manual",
        },
    ]

    # 创建赛事
    for data in contests_data:
        contest = Contest(
            id=str(uuid.uuid4()),
            **data
        )
        db.add(contest)

    db.commit()
    print(f"已初始化 {len(contests_data)} 个赛事数据")


def init_static_team_data(db: Session, user_id: str = "static_user_1") -> None:
    """初始化静态队伍假数据"""
    from sqlalchemy import func

    # 获取几个赛事
    contests = db.query(Contest).limit(4).all()
    if not contests:
        return

    # 检查是否已有队伍
    existing = db.query(Team).first()
    if existing:
        print("已有队伍数据，跳过初始化")
        return

    team_names = [
        "超能战队", "代码艺术家", "机械之心", "创新者联盟"
    ]

    for i, contest in enumerate(contests):
        team = Team(
            id=str(uuid.uuid4()),
            contest_id=contest.id,
            name=team_names[i],
            description=f"我们是一支充满激情的队伍，擅长{['算法设计', '软件开发', '硬件制作', '创意设计'][i]}！",
            max_members=5,
            required_skills=[["Python", "C++"], ["Java", "前端"], ["SolidWorks", "电路"], ["PS", "视频"]][i],
            status=TeamStatus.RECRUITING,
        )
        db.add(team)
        db.flush()

        # 添加队长
        member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=team.id,
            user_id=user_id,
            role=TeamMemberRole.LEADER,
        )
        db.add(member)

        # 更新赛事组队数量
        contest.team_count = (contest.team_count or 0) + 1

    db.commit()
    print(f"已初始化 {len(team_names)} 个队伍数据")
