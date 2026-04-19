"""修复附件表url字段长度"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import engine
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    print("开始迁移数据库...")

    with engine.connect() as conn:
        # 修改 url 字段为 TEXT
        sql = "ALTER TABLE contest_attachments MODIFY COLUMN url TEXT COMMENT '原始URL'"
        print(f"执行: {sql}")
        conn.execute(text(sql))
        conn.commit()
        print("✓ 已修改 url 字段为 TEXT")

    print("\n迁移完成！")


if __name__ == "__main__":
    migrate()
