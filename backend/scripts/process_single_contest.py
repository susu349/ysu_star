#!/usr/bin/env python3
"""处理单个特定的赛事"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from campus_ai.core.config import get_settings
from campus_ai.services.contest import ContestAIProcessor, ContestPreprocessor
from campus_ai.models import Contest

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    contest_id = "db18cc09-3935-4dfc-a0d1-df5622c6fd95"

    contest = db.query(Contest).filter(Contest.id == contest_id).first()

    if contest:
        print(f"处理赛事: {contest.title}")
        print(f"当前 is_ai_processed: {contest.is_ai_processed}")
        print(f"当前 brief_description: {contest.brief_description}")
        print()

        # 先用规则预处理
        preprocessor = ContestPreprocessor()
        content = contest.raw_content or contest.description or ""
        print(f"内容长度: {len(content)} 字符")

        if content:
            print("正在用规则预处理...")
            extracted = preprocessor.preprocess_contest(contest.title, content)

            print("提取结果:")
            for key, value in extracted.items():
                if value:
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")

            # 更新赛事
            print("\n正在更新数据库...")

            for key, value in extracted.items():
                if hasattr(contest, key) and value:
                    setattr(contest, key, value)

            contest.is_ai_processed = True
            contest.needs_review = False

            db.commit()
            db.refresh(contest)

            print("完成！")
            print(f"新的 brief_description: {contest.brief_description[:100]}...")
        else:
            print("没有内容可以处理")
    else:
        print(f"未找到 ID 为 {contest_id} 的赛事")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
