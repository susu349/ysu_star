"""创建测试用户"""
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
        # 检查用户是否已存在
        existing = db.query(User).filter(User.username == "test").first()
        if existing:
            print(f"用户 'test' 已存在")
            print(f"用户名: test")
            print(f"密码: test123456")
            return

        # 创建用户
        user = User(
            id="test_user_001",
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
        db.add(user)
        db.commit()
        db.refresh(user)

        print("\n测试用户创建成功！")
        print("=" * 60)
        print(f"用户名: test")
        print(f"密码: test123456")
        print(f"姓名: 测试用户")
        print(f"角色: 学生")
        print(f"院系: 信息科学与工程学院")
        print(f"专业: 计算机科学与技术")
        print(f"年级: 2021")
        print("=" * 60)
        print("\n现在可以用这个账号登录前端了！")

    finally:
        db.close()


if __name__ == "__main__":
    create_user()
