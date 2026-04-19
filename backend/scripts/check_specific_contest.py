#!/usr/bin/env python3
"""查看特定赛事的数据"""
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
    contest_id = "db18cc09-3935-4dfc-a0d1-df5622c6fd95"

    result = db.execute(text("""
        SELECT id, title, summary, brief_description, description,
               source_url
        FROM contests
        WHERE id = :cid
    """), {"cid": contest_id})
    contest = result.fetchone()

    if contest:
        print("=" * 100)
        print(f"赛事: {contest[1]}")
        print("=" * 100)
        print(f"\n[1] summary: {contest[2] or '空'}")
        print(f"\n[2] brief_description: {contest[3] or '空'}")
        print(f"\n[3] description (前500字符): {contest[4][:500] if contest[4] else '空'}...")
        print(f"\n[4] source_url: {contest[5] or '空'}")

        # 检查附件
        print("\n" + "=" * 100)
        print("附件信息:")
        print("=" * 100)
        attach_result = db.execute(text("""
            SELECT id, name, url, file_type, file_size, is_downloaded
            FROM contest_attachments
            WHERE contest_id = :cid
        """), {"cid": contest_id})
        attachments = attach_result.fetchall()
        if attachments:
            for a in attachments:
                print(f"- {a[1]} ({a[3]}, {a[4] or '?'} bytes)")
        else:
            print("无附件")

    else:
        print(f"未找到 ID 为 {contest_id} 的赛事")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
