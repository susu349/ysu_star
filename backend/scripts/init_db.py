"""
数据库初始化脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import engine, Base, SessionLocal
from campus_ai.core.config import get_settings
from campus_ai.models import *
from campus_ai.services.contest import init_static_contest_data, init_static_team_data

settings = get_settings()


def init_db():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def init_data():
    """初始化静态数据"""
    print("正在初始化静态赛事数据...")
    db = SessionLocal()
    try:
        init_static_contest_data(db)
        init_static_team_data(db)
        print("静态数据初始化完成！")
    finally:
        db.close()


def drop_tables():
    """删除所有表（谨慎使用）"""
    print("正在删除所有数据库表...")
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成！")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库管理脚本")
    parser.add_argument(
        "action",
        choices=["init", "drop", "reinit", "data"],
        help="操作: init(创建表), drop(删除表), reinit(重建表), data(初始化数据)"
    )

    args = parser.parse_args()

    if args.action == "init":
        init_db()
    elif args.action == "drop":
        drop_tables()
    elif args.action == "reinit":
        drop_tables()
        init_db()
        init_data()
    elif args.action == "data":
        init_data()
