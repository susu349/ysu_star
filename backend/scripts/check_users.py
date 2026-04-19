"""检查现有用户"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import User


def check():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"数据库中共有 {len(users)} 个用户\n")

        if users:
            for i, u in enumerate(users, 1):
                print(f"[{i}]")
                print(f"  用户名: {u.username}")
                print(f"  姓名: {u.real_name}")
                print(f"  角色: {u.role}")
                print(f"  激活: {u.is_active}")
                print(f"  ID: {u.id}")
                print()
        else:
            print("没有用户！")
            print("需要先创建用户。")

    finally:
        db.close()


if __name__ == "__main__":
    check()
