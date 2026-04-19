#!/usr/bin/env python3
"""查看赛事详情数据示例"""
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
        SELECT id, title, summary, brief_description, description,
               eligibility_requirements, participation_process,
               awards_info, recommendations, contact_info
        FROM contests
        WHERE is_ai_processed = TRUE
        LIMIT 1
    """))
    contest = result.fetchone()

    if contest:
        print("=" * 100)
        print(f"赛事: {contest[1]}")
        print("=" * 100)
        print(f"\n[1] summary: {contest[2][:200] if contest[2] else '空'}...")
        print(f"\n[2] brief_description: {contest[3][:200] if contest[3] else '空'}...")
        print(f"\n[3] description: {contest[4][:200] if contest[4] else '空'}...")
        print(f"\n[4] eligibility_requirements: {contest[5][:200] if contest[5] else '空'}...")
        print(f"\n[5] participation_process: {contest[6][:200] if contest[6] else '空'}...")
        print(f"\n[6] awards_info: {contest[7][:200] if contest[7] else '空'}...")
        print(f"\n[7] recommendations: {contest[8][:200] if contest[8] else '空'}...")
        print(f"\n[8] contact_info: {contest[9][:200] if contest[9] else '空'}...")

        # 检查附件
        print("\n" + "=" * 100)
        print("附件信息:")
        print("=" * 100)
        attach_result = db.execute(text("""
            SELECT id, name, url, file_type, file_size, is_downloaded
            FROM contest_attachments
            WHERE contest_id = :cid
        """), {"cid": contest[0]})
        attachments = attach_result.fetchall()
        if attachments:
            for a in attachments:
                print(f"- {a[1]} ({a[3]}, {a[4] or '?'} bytes)")
        else:
            print("无附件")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
