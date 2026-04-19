"""检查未发布的赛事"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import Contest


def check():
    db = SessionLocal()
    try:
        unpublished = db.query(Contest).filter(Contest.status != "published").all()

        print(f"未发布的赛事: {len(unpublished)} 个\n")

        for i, c in enumerate(unpublished, 1):
            print(f"[{i}] {c.title[:60]}")
            print(f"    状态: {c.status}")
            print(f"    已AI处理: {c.is_ai_processed}")
            print(f"    需要复核: {c.needs_review}")
            print()

    finally:
        db.close()


if __name__ == "__main__":
    check()
