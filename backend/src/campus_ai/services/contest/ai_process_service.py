"""
赛事AI处理服务 - 调用LLM进行智能信息提取
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...models import Contest, ContestStatus, ContestLevel, ContestAttachment
from .preprocess_service import ContestPreprocessor
from .attachment_service import AttachmentService
from ...core.utils.llm_client import LLMClient
from ...core.config import get_settings

settings = get_settings()


class ContestAIProcessor:
    """赛事AI处理器"""

    def __init__(self, db: Session, use_llm: bool = True):
        self.db = db
        self.preprocessor = ContestPreprocessor()
        self.attachment_service = AttachmentService(db)
        self.use_llm = use_llm and settings.LLM_API_KEY
        if self.use_llm:
            self.llm_client = LLMClient(api_key=settings.LLM_API_KEY)

    def _get_attachment_contents(self, contest: Contest) -> str:
        """获取并解析所有附件内容"""
        contents = []
        attachments = self.attachment_service.get_attachments_by_contest(contest.id)

        for att in attachments:
            content = self.attachment_service.get_attachment_content(att)
            if content:
                contents.append(f"=== 附件：{att.name} ===\n{content}")

        return "\n\n".join(contents) if contents else ""

    def process_contest(self, contest_id: str) -> Optional[Contest]:
        """AI处理赛事信息"""
        contest = self.db.query(Contest).filter(Contest.id == contest_id).first()
        if not contest:
            return None

        content = contest.raw_content or contest.description or ""
        title = contest.title or ""

        # 获取附件内容
        attachment_content = self._get_attachment_contents(contest)

        if self.use_llm and content:
            # 优先用LLM提取
            extracted = self._extract_with_llm(title, content, attachment_content)
            if extracted:
                self._update_contest_from_dict(contest, extracted)
                contest.is_ai_processed = True
                contest.needs_review = False
            else:
                # LLM失败，回退到规则
                extracted = self.preprocessor.preprocess_contest(title, content)
                self._update_contest_from_dict(contest, extracted)
        else:
            # 只用规则提取
            extracted = self.preprocessor.preprocess_contest(title, content)
            self._update_contest_from_dict(contest, extracted)

        # 自动设置状态
        if contest.status == ContestStatus.DRAFT and not contest.needs_review:
            contest.status = ContestStatus.PUBLISHED

        self.db.commit()
        self.db.refresh(contest)
        return contest

    def _extract_with_llm(self, title: str, content: str, attachment_content: str = "") -> Optional[Dict[str, Any]]:
        """用LLM提取结构化信息"""
        # 构建内容
        full_content = content[:4000]
        if attachment_content:
            full_content += f"\n\n【附件内容】\n{attachment_content[:3000]}"

        prompt = f"""
请从以下赛事信息中提取结构化数据。请综合网页内容和附件内容进行判断。

赛事标题：{title}

赛事内容：
{full_content}

请返回扁平的JSON格式（不要嵌套），包含以下字段：

- summary: 100字以内的极简摘要，只保留学生决策最需要的核心信息
- level: 赛事级别，只能是这四个值之一："school"(校赛), "province"(省赛), "national"(国赛), "international"(国际赛)
- category: 赛事分类，可选值："科技创新", "创新创业", "程序设计", "数学建模", "电子设计", "机械设计", "计算机设计", "节能减排", "其他"
- tags: 相关标签数组，3-5个
- organizer: 主办方（如果有）
- registration_start: 报名开始日期，格式"YYYY-MM-DD"（如果有）
- registration_end: 报名截止日期，格式"YYYY-MM-DD"（如果有）
- contest_start: 比赛开始日期，格式"YYYY-MM-DD"（如果有）
- contest_end: 比赛结束日期，格式"YYYY-MM-DD"（如果有）
- brief_description: 简洁说明，200字左右，适合在卡片展示，让学生快速了解这个比赛是什么
- eligibility_requirements: 参赛资格，说明谁可以参加（专业、年级、人数限制等）
- participation_process: 参赛流程，分步骤说明怎么报名、提交作品等
- awards_info: 奖项信息，有什么奖项、奖品、学分认定等
- contact_info: 联系方式，整理成清晰格式，包括联系人、电话、邮箱、QQ、微信群等
- recommendations: 推荐建议，适合什么类型的学生参加、如何备赛、注意事项等

注意：
1. 日期如果是相对时间（比如"即日起"），可以用null
2. 不确定的字段用null
3. 字符串字段如果信息不足可以用null，但尽量从内容中提取
4. 只返回JSON，不要其他文本，不要嵌套结构
5. 所有中文字符串请用中文返回
"""

        messages = [{"role": "user", "content": prompt}]

        try:
            result = self.llm_client.chat_with_json(messages, temperature=0.1)
            if result:
                # 如果是嵌套结构，展平它
                if "基础信息" in result:
                    # 处理嵌套结构
                    flat = {}
                    flat.update(result.get("基础信息", {}))
                    flat.update(result.get("时间信息", {}))
                    flat.update(result.get("详细信息", {}))
                    result = flat

                # 转换日期字符串为datetime对象
                for date_field in ["registration_start", "registration_end", "contest_start", "contest_end"]:
                    if result.get(date_field) and isinstance(result[date_field], str):
                        try:
                            result[date_field] = datetime.fromisoformat(result[date_field])
                        except (ValueError, TypeError):
                            result[date_field] = None
                # 转换level为枚举
                if result.get("level"):
                    level_map = {
                        "school": ContestLevel.SCHOOL,
                        "province": ContestLevel.PROVINCE,
                        "national": ContestLevel.NATIONAL,
                        "international": ContestLevel.INTERNATIONAL,
                    }
                    result["level"] = level_map.get(result["level"], ContestLevel.SCHOOL)
            return result
        except Exception as e:
            print(f"LLM提取失败: {e}")
            return None

    def _update_contest_from_dict(self, contest: Contest, data: Dict[str, Any]):
        """从字典更新赛事信息"""
        # 基础字段
        fields = [
            "summary", "level", "category", "tags", "organizer",
            "registration_start", "registration_end",
            "contest_start", "contest_end",
            "contact",  # 联系字段已存在
        ]
        for field in fields:
            if field in data and data[field] is not None:
                setattr(contest, field, data[field])

        # 新增的详细信息字段
        detail_fields = [
            "brief_description",
            "eligibility_requirements",
            "participation_process",
            "awards_info",
            "contact_info",
            "recommendations",
        ]
        for field in detail_fields:
            if field in data and data[field] is not None:
                setattr(contest, field, data[field])

    def batch_process_contests(self, limit: int = 10) -> int:
        """批量处理未处理的赛事"""
        contests = self.db.query(Contest).filter(
            Contest.is_ai_processed == False,
            Contest.raw_content != None
        ).limit(limit).all()

        processed = 0
        for contest in contests:
            try:
                self.process_contest(contest.id)
                processed += 1
            except Exception as e:
                print(f"处理赛事 {contest.id} 失败: {e}")
                contest.needs_review = True
                self.db.commit()

        return processed

    def close(self):
        if self.use_llm:
            self.llm_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
