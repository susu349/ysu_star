"""创建简单易记的测试用户"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import User
from campus_ai.core.security import get_password_hash


def create_users():
    """创建测试用户"""
    print("=" * 60)
    print("创建易记的测试用户")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 删除所有现有用户
        old_users = db.query(User).all()
        print(f"删除 {len(old_users)} 个旧用户...")
        for u in old_users:
            db.delete(u)
        db.commit()

        # 创建管理员账号 - 学号/工号: admin
        admin = User(
            id="admin",
            username="admin",
            email="admin@ysu.edu.cn",
            hashed_password=get_password_hash("admin123"),
            real_name="测试管理员",
            role="admin",
            department="信息科学与工程学院",
            major="计算机科学与技术",
            grade="2021",
            is_active=True,
            is_verified=True,
        )
        db.add(admin)

        # 创建学生账号 - 学号: 2021001
        student = User(
            id="2021001",
            username="test",
            email="test@ysu.edu.cn",
            hashed_password=get_password_hash("123456"),
            real_name="张三",
            role="student",
            department="信息科学与工程学院",
            major="计算机科学与技术",
            grade="2021",
            is_active=True,
            is_verified=True,
        )
        db.add(student)

        db.commit()

        print("\n✅ 测试用户创建成功！")
        print("=" * 60)
        print("【管理员账号】")
        print(f"  学号/工号: admin")
        print(f"  密码: admin123")
        print()
        print("【学生账号】")
        print(f"  学号/工号: 2021001")
        print(f"  密码: 123456")
        print("=" * 60)
        print("\n注意：登录时使用 '学号/工号' 字段，不是 'username'！")

    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_users()
