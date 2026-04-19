#!/usr/bin/env python3
"""添加私信表的迁移脚本"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import engine, Base
from campus_ai.models.contest import PrivateMessage

print("正在创建私信表...")
Base.metadata.create_all(bind=engine, tables=[PrivateMessage.__table__])
print("私信表创建完成！")
