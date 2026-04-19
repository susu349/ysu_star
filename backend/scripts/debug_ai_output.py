"""调试LLM返回"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
from campus_ai.core.database import SessionLocal
from campus_ai.models import Contest
from campus_ai.core.utils.llm_client import LLMClient
from campus_ai.core.config import get_settings

settings = get_settings()


def debug_llm():
    """调试LLM返回"""
    print("=" * 80)
    print("调试LLM返回")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 找一个赛事
        contest = db.query(Contest).first()
        if not contest:
            print("没有赛事")
            return

        title = contest.title or ""
        content = contest.raw_content or ""

        print(f"\n标题: {title[:60]}")
        print(f"内容长度: {len(content)}")

        # 构建 Prompt
        full_content = content[:4000]
        prompt = f"""
请从以下赛事信息中提取结构化数据。

赛事标题：{title}

赛事内容：
{full_content}

请返回JSON格式，包含以下字段：

基础信息：
- summary: 100字以内的极简摘要
- level: 赛事级别，只能是这四个值之一："school"(校赛), "province"(省赛), "national"(国赛), "international"(国际赛)
- category: 赛事分类，可选值："科技创新", "创新创业", "程序设计", "数学建模", "电子设计", "机械设计", "计算机设计", "节能减排", "其他"
- tags: 相关标签数组，3-5个
- organizer: 主办方（如果有）

时间信息：
- registration_start: 报名开始日期，格式"YYYY-MM-DD"（如果有）
- registration_end: 报名截止日期，格式"YYYY-MM-DD"（如果有）
- contest_start: 比赛开始日期，格式"YYYY-MM-DD"（如果有）
- contest_end: 比赛结束日期，格式"YYYY-MM-DD"（如果有）

详细信息（这些是字符串，100-300字）：
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
4. 只返回JSON，不要其他文本
5. 所有中文字符串请用中文返回
"""

        print(f"\nPrompt长度: {len(prompt)}")
        print("\n调用LLM...")

        llm_client = LLMClient(api_key=settings.LLM_API_KEY)
        messages = [{"role": "user", "content": prompt}]
        result = llm_client.chat_with_json(messages, temperature=0.1)

        print(f"\nLLM返回:")
        print("-" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        print(f"\n字段检查:")
        fields = [
            "summary", "level", "category", "tags", "organizer",
            "registration_start", "registration_end", "contest_start", "contest_end",
            "brief_description", "eligibility_requirements", "participation_process",
            "awards_info", "contact_info", "recommendations",
        ]
        for f in fields:
            has = "✓" if f in result and result[f] is not None else "✗"
            val = str(result.get(f, ""))[:50] if result.get(f) else ""
            print(f"  {has} {f:30} {val}")

        llm_client.close()

    finally:
        db.close()


if __name__ == "__main__":
    debug_llm()
