"""演示AI处理的完整流程：输入 -> LLM -> 解析 -> 入库"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime
from campus_ai.core.database import SessionLocal
from campus_ai.models import Contest, ContestLevel, ContestStatus
from campus_ai.core.utils.llm_client import LLMClient
from campus_ai.core.config import get_settings

settings = get_settings()


def demo_ai_flow():
    """演示AI处理流程"""
    print("=" * 80)
    print("AI处理流程演示")
    print("=" * 80)

    # 1. 模拟输入（网页内容 + 附件内容）
    print("\n【步骤1】输入数据")
    print("-" * 80)
    title = "关于举办第十九届全国三维数字化创新设计大赛燕山大学选拔赛的通知"
    content = """全校师生：
全国三维数字化创新设计大赛是学校认定的一类创新创业竞赛。根据全国三维数字化创新设计大赛组委会相关文件精神，决定举办第十九届全国三维数字化创新设计大赛燕山大学选拔赛，具体事宜如下：

一、赛项设置
（一）开放赛项
下设四大竞赛方向及评审赛项：
1、数字工业设计大赛
2、数字人居设计大赛
3、数字文化设计大赛
4、数字元宇宙设计大赛

二、参赛对象
我校全日制在校本科生、研究生。

三、时间安排
1. 报名截止时间：2026年6月30日
2. 复赛/省赛选拔：9月1日-10月31日
3. 国赛/全国总决赛：11月-12月

四、联系方式
本届大赛校内选拔赛由机械工程学院负责组织。
联系人：刘丰13102535739

创新创业教育与指导中心
机械工程学院
2026年4月17日
"""
    print(f"标题: {title}")
    print(f"内容长度: {len(content)} 字符")

    # 2. 构建 Prompt
    print("\n【步骤2】构建 Prompt")
    print("-" * 80)
    prompt = f"""
请从以下赛事信息中提取结构化数据。

赛事标题：{title}

赛事内容：
{content[:4000]}

请返回JSON格式，包含以下字段：
- summary: 100字以内的极简摘要
- level: 赛事级别，只能是这四个值之一："school"(校赛), "province"(省赛), "national"(国赛), "international"(国际赛)
- category: 赛事分类，可选值："科技创新", "创新创业", "程序设计", "数学建模", "电子设计", "机械设计", "计算机设计", "节能减排", "其他"
- tags: 相关标签数组，3-5个
- organizer: 主办方（如果有）
- registration_start: 报名开始日期，格式"YYYY-MM-DD"（如果有）
- registration_end: 报名截止日期，格式"YYYY-MM-DD"（如果有）
- contest_start: 比赛开始日期，格式"YYYY-MM-DD"（如果有）
- contest_end: 比赛结束日期，格式"YYYY-MM-DD"（如果有）

注意：
1. 日期如果是相对时间（比如"即日起"），可以用null
2. 不确定的字段用null
3. 只返回JSON，不要其他文本
"""
    print(prompt[:500], "...")

    # 3. 调用 LLM
    print("\n【步骤3】调用 LLM")
    print("-" * 80)
    llm_client = LLMClient(api_key=settings.LLM_API_KEY)

    messages = [{"role": "user", "content": prompt}]
    result = llm_client.chat_with_json(messages, temperature=0.1)

    print("LLM 返回的 JSON:")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 4. 类型转换
    print("\n【步骤4】类型转换（字符串 -> Python 对象）")
    print("-" * 80)
    if result:
        # 日期转换：字符串 -> datetime
        for date_field in ["registration_start", "registration_end", "contest_start", "contest_end"]:
            if result.get(date_field) and isinstance(result[date_field], str):
                try:
                    result[date_field] = datetime.fromisoformat(result[date_field])
                    print(f"  {date_field}: {result[date_field]} (datetime)")
                except (ValueError, TypeError):
                    result[date_field] = None

        # Level 转换：字符串 -> Enum
        if result.get("level"):
            level_map = {
                "school": ContestLevel.SCHOOL,
                "province": ContestLevel.PROVINCE,
                "national": ContestLevel.NATIONAL,
                "international": ContestLevel.INTERNATIONAL,
            }
            result["level"] = level_map.get(result["level"], ContestLevel.SCHOOL)
            print(f"  level: {result['level']} (Enum)")

    # 5. 入库
    print("\n【步骤5】入库（更新数据库字段）")
    print("-" * 80)
    db = SessionLocal()

    # 找一个现有的赛事来演示更新
    contest = db.query(Contest).first()
    if not contest:
        print("没有赛事，先创建一个...")
        import uuid
        contest = Contest(
            id=str(uuid.uuid4()),
            title=title,
            raw_content=content,
            level=ContestLevel.SCHOOL,
            category="科技创新",
            status=ContestStatus.DRAFT,
            source="crawler",
            is_ai_processed=False,
            needs_review=True,
        )
        db.add(contest)
        db.commit()
        db.refresh(contest)

    print(f"更新前:")
    print(f"  summary: {contest.summary}")
    print(f"  level: {contest.level}")
    print(f"  category: {contest.category}")
    print(f"  tags: {contest.tags}")
    print(f"  organizer: {contest.organizer}")
    print(f"  registration_end: {contest.registration_end}")

    # 更新字段
    fields = [
        "summary", "level", "category", "tags", "organizer",
        "registration_start", "registration_end",
        "contest_start", "contest_end"
    ]
    for field in fields:
        if field in result and result[field] is not None:
            setattr(contest, field, result[field])

    contest.is_ai_processed = True
    contest.needs_review = False
    if contest.status == ContestStatus.DRAFT:
        contest.status = ContestStatus.PUBLISHED

    db.commit()
    db.refresh(contest)

    print(f"\n更新后:")
    print(f"  summary: {contest.summary}")
    print(f"  level: {contest.level}")
    print(f"  category: {contest.category}")
    print(f"  tags: {contest.tags}")
    print(f"  organizer: {contest.organizer}")
    print(f"  registration_end: {contest.registration_end}")
    print(f"  is_ai_processed: {contest.is_ai_processed}")
    print(f"  status: {contest.status}")

    llm_client.close()
    db.close()

    print("\n" + "=" * 80)
    print("流程结束！")
    print("=" * 80)


if __name__ == "__main__":
    demo_ai_flow()
