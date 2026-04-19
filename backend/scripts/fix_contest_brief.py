#!/usr/bin/env python3
"""修复赛事简介，用 summary 填充 brief_description"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from campus_ai.core.config import get_settings
from campus_ai.models import Contest

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    contests = db.query(Contest).filter(
        (Contest.brief_description == None) | (Contest.brief_description == '')
    ).all()

    print(f"找到 {len(contests)} 个没有简介的赛事")

    updated_count = 0
    for contest in contests:
        if contest.summary and contest.summary.strip():
            contest.brief_description = contest.summary
            contest.is_ai_processed = True
            updated_count += 1

    db.commit()
    print(f"已更新 {updated_count} 个赛事的简介")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
