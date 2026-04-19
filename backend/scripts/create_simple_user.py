"""创建简单测试用户（不依赖bcrypt）"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import User


def create_user():
    """创建测试用户"""
    print("=" * 60)
    print("创建测试用户")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 检查用户是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"用户 'admin' 已存在")
            print(f"用户名: admin")
            print(f"密码: admin123")
            return existing

        # 创建用户（使用一个简单的哈希占位符）
        user = User(
            id="admin_user_001",
            username="admin",
            email="admin@ysu.edu.cn",
            # 临时占位符（不能用来登录，但先创建用户记录）
            hashed_password="not_hashed_yet",
            real_name="管理员",
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

        print("\n用户记录创建成功！")
        print("=" * 60)
        print(f"用户名: admin")
        print(f"密码: admin123 (需要修复bcrypt后才能登录)")
        print(f"姓名: 管理员")
        print(f"角色: 管理员")
        print("=" * 60)
        print("\n提示：可以先直接访问以下不需要登录的API：")
        print("  - 赛事列表: http://localhost:8000/api/v1/contest/list")
        print("  - API文档: http://localhost:8000/docs")

        return user

    finally:
        db.close()


if __name__ == "__main__":
    create_user()
