#!/usr/bin/env python3
"""对所有没有 AI 处理的赛事进行处理"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from campus_ai.core.config import get_settings
from campus_ai.services.contest import ContestAIProcessor

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 找出未处理的赛事
    result = db.execute(text("""
        SELECT id, title
        FROM contests
        WHERE is_ai_processed = FALSE OR is_ai_processed IS NULL
        ORDER BY created_at DESC
    """))
    contests = result.fetchall()

    print(f"找到 {len(contests)} 个未处理的赛事")

    processor = ContestAIProcessor(db)

    for i, contest in enumerate(contests, 1):
        print(f"[{i}/{len(contests)}] 处理: {contest[1][:50]}...")
        try:
            processor.process_contest(contest[0])
            print(f"  ✓ 完成")
        except Exception as e:
            print(f"  ✗ 失败: {e}")

    print("\n所有赛事处理完成!")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
