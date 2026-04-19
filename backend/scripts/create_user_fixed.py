"""创建测试用户（修复bcrypt后）"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import User
from campus_ai.core.security import get_password_hash


def create_user():
    """创建测试用户"""
    print("=" * 60)
    print("创建测试用户")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 先删除旧的admin用户
        old_user = db.query(User).filter(User.username == "admin").first()
        if old_user:
            print(f"删除旧用户: {old_user.username}")
            db.delete(old_user)
            db.commit()

        # 创建新用户
        user = User(
            id="test_user_001",
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
        db.add(user)
        db.commit()
        db.refresh(user)

        print("\n✅ 测试用户创建成功！")
        print("=" * 60)
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"姓名: 测试管理员")
        print(f"角色: 管理员")
        print("=" * 60)
        print("\n现在可以用这个账号登录前端了！")
        print("前端地址: http://localhost:3000")

        return user

    finally:
        db.close()


if __name__ == "__main__":
    create_user()
