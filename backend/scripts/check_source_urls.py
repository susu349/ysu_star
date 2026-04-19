#!/usr/bin/env python3
"""检查 source_url 的格式"""
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
    result = db.execute(text("SELECT id, title, source_url FROM contests WHERE source_url IS NOT NULL LIMIT 20"))
    contests = result.fetchall()

    print("前20条赛事的 source_url:")
    print("-" * 100)
    for c in contests:
        print(f"ID: {c[0][:10]}...")
        print(f"标题: {c[1][:50]}...")
        print(f"URL: {c[2]}")
        print()

except Exception as e:
    print(f"错误: {e}")
finally:
    db.close()
