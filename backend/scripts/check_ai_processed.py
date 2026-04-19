#!/usr/bin/env python3
"""检查哪些赛事有 AI 处理后的数据"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from campus_ai.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    result = db.execute(text("""
        SELECT id, title,
               CASE WHEN brief_description IS NOT NULL AND brief_description != '' THEN 'YES' ELSE 'NO' END as has_brief,
               CASE WHEN description IS NOT NULL AND description != '' THEN 'YES' ELSE 'NO' END as has_desc,
               CASE WHEN eligibility_requirements IS NOT NULL AND eligibility_requirements != '' THEN 'YES' ELSE 'NO' END as has_eligibility,
               is_ai_processed
        FROM contests
        ORDER BY created_at DESC
        LIMIT 10
    """))
    contests = result.fetchall()

    print("最近 10 个赛事的数据情况:")
    print("-" * 120)
    print(f"{'ID':<8} {'标题':<30} {'简介':<6} {'原始':<6} {'资格':<6} {'AI处理':<6}")
    print("-" * 120)
    for c in contests:
        print(f"{c[0][:8]:<8} {c[1][:28]:<30} {c[2]:<6} {c[3]:<6} {c[4]:<6} {str(c[5]):<6}")

    # 找一个有完整数据的
    print("\n" + "=" * 120)
    print("找一个有完整 AI 处理数据的赛事:")
    print("=" * 120)
    result = db.execute(text("""
        SELECT id, title, brief_description
        FROM contests
        WHERE brief_description IS NOT NULL AND brief_description != ''
        ORDER BY created_at DESC
        LIMIT 1
    """))
    contest = result.fetchone()
    if contest:
        print(f"ID: {contest[0]}")
        print(f"标题: {contest[1]}")
        print(f"Brief: {contest[2][:200]}...")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
