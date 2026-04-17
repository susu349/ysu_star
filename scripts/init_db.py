#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend/src"))

from sqlalchemy import create_engine, text
from campus_ai.core.database import Base
from campus_ai.models.user import User

# 直接用 root 连接
DB_URL = "mysql+pymysql://root@localhost:3306/mysql?charset=utf8mb4"
engine = create_engine(DB_URL)

print("正在创建数据库...")
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS campus_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    conn.commit()

print("数据库创建成功！")

# 现在连接到新数据库创建表
from campus_ai.core.config import get_settings
settings = get_settings()

engine = create_engine(settings.DATABASE_URL)

print("正在创建数据表...")
Base.metadata.create_all(bind=engine)

print("✅ 所有表创建成功！")
print("")
print("数据库配置:")
print(f"  数据库名: {settings.MYSQL_DATABASE}")
print(f"  用户: root")
print("")
