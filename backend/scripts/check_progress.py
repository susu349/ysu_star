"""快速检查进度"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import Contest


def check():
    db = SessionLocal()
    try:
        total = db.query(Contest).count()
        processed = db.query(Contest).filter(Contest.is_ai_processed == True).count()
        published = db.query(Contest).filter(Contest.status == "published").count()

        print("=" * 60)
        print("数据库进度")
        print("=" * 60)
        print(f"  总赛事数: {total}")
        print(f"  已AI处理: {processed}")
        print(f"  已发布: {published}")
        print(f"  待处理: {total - processed}")
        print("=" * 60)

        # 查看最新处理的一个
        latest = db.query(Contest).filter(Contest.is_ai_processed == True).order_by(Contest.updated_at.desc()).first()
        if latest:
            print(f"\n最新处理:")
            print(f"  标题: {latest.title[:60]}...")
            print(f"  级别: {latest.level}")
            print(f"  分类: {latest.category}")

    finally:
        db.close()


if __name__ == "__main__":
    check()
