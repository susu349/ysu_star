"""添加新字段到 contests 表"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import engine, Base
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    print("开始迁移数据库...")

    with engine.connect() as conn:
        # 检查字段是否已存在
        check_sql = """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'contests'
        AND COLUMN_NAME IN (
            'brief_description',
            'participation_process',
            'contact_info',
            'recommendations',
            'eligibility_requirements',
            'awards_info'
        )
        """
        result = conn.execute(text(check_sql))
        existing_columns = {row[0] for row in result}
        print(f"已存在的字段: {existing_columns}")

        # 添加新字段
        new_columns = [
            ("brief_description", "TEXT", "简洁说明：200-300字，适合卡片展示"),
            ("participation_process", "TEXT", "参赛流程：分步骤说明"),
            ("contact_info", "TEXT", "联系方式：联系人、电话、邮箱、QQ等"),
            ("recommendations", "TEXT", "推荐建议：适合人群、备赛建议、注意事项"),
            ("eligibility_requirements", "TEXT", "参赛资格：专业、年级、人数限制等"),
            ("awards_info", "TEXT", "奖项信息：奖项设置、奖品、学分认定等"),
        ]

        for col_name, col_type, col_comment in new_columns:
            if col_name not in existing_columns:
                sql = f"ALTER TABLE contests ADD COLUMN {col_name} {col_type} COMMENT '{col_comment}'"
                print(f"执行: {sql}")
                conn.execute(text(sql))
                print(f"  ✓ 已添加字段: {col_name}")
            else:
                print(f"  - 字段已存在，跳过: {col_name}")

        conn.commit()

    print("\n迁移完成！")


if __name__ == "__main__":
    migrate()
