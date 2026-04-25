"""重置所有测试用户"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import User
from campus_ai.core.security import get_password_hash


def reset_users():
    """重置测试用户"""
    print("=" * 60)
    print("重置测试用户")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 删除所有现有用户
        old_users = db.query(User).all()
        print(f"删除 {len(old_users)} 个旧用户...")
        for u in old_users:
            db.delete(u)
        db.commit()

        # 创建管理员账号
        admin = User(
            id=str(uuid.uuid4()),
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

        # 创建学生账号
        student = User(
            id=str(uuid.uuid4()),
            username="test",
            email="test@ysu.edu.cn",
            hashed_password=get_password_hash("test123456"),
            real_name="测试用户",
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
        print(f"  用户名: admin")
        print(f"  密码: admin123")
        print()
        print("【学生账号】")
        print(f"  用户名: test")
        print(f"  密码: test123456")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_users()
