#!/usr/bin/env python3
"""检查数据库中的赛事数据"""
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
    result = db.execute(text("SELECT COUNT(*) FROM contests"))
    count = result.scalar()
    print(f"数据库中共有 {count} 个赛事\n")

    result = db.execute(text("SELECT id, title, level, status, category, organizer, created_at FROM contests ORDER BY created_at DESC LIMIT 10"))
    contests = result.fetchall()

    print("最新的10个赛事:")
    print("-" * 100)
    for c in contests:
        print(f"ID: {c[0]}")
        print(f"标题: {c[1]}")
        print(f"级别: {c[2]}")
        print(f"状态: {c[3]}")
        print(f"分类: {c[4]}")
        print(f"主办方: {c[5]}")
        print(f"创建时间: {c[6]}")
        print("-" * 100)

except Exception as e:
    print(f"错误: {e}")
finally:
    db.close()
