#!/usr/bin/env python3
"""添加评论表的迁移脚本"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import engine, Base
from campus_ai.models.contest import ContestComment

print("正在创建评论表...")
Base.metadata.create_all(bind=engine, tables=[ContestComment.__table__])
print("评论表创建完成！")
