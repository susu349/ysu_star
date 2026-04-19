"""展示整理好的赛事数据"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.models import Contest


def show_data():
    """展示数据"""
    print("=" * 80)
    print("赛事数据库展示")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 统计数据
        total = db.query(Contest).count()
        ai_processed = db.query(Contest).filter(Contest.is_ai_processed == True).count()
        published = db.query(Contest).filter(Contest.status == "published").count()

        print(f"\n统计:")
        print(f"  总赛事数: {total}")
        print(f"  已AI处理: {ai_processed}")
        print(f"  已发布: {published}")

        # 展示前3个已AI处理的赛事
        print(f"\n" + "=" * 80)
        print("已处理的赛事详情 (前3个)")
        print("=" * 80)

        contests = db.query(Contest).filter(Contest.is_ai_processed == True).limit(3).all()

        if not contests:
            print("\n还没有已AI处理的赛事，后台任务正在运行中...")
            contests = db.query(Contest).limit(3).all()
            if contests:
                print(f"\n展示已爬取的 {len(contests)} 个赛事:")

        for i, contest in enumerate(contests, 1):
            print(f"\n【赛事 {i}】")
            print("-" * 80)
            print(f"标题: {contest.title[:80]}")
            print(f"ID: {contest.id}")
            print(f"来源: {contest.source_url}")

            if contest.is_ai_processed:
                print(f"\nAI处理结果:")
                print(f"  摘要: {contest.summary}")
                print(f"  级别: {contest.level}")
                print(f"  分类: {contest.category}")
                print(f"  标签: {contest.tags}")
                print(f"  主办方: {contest.organizer}")
                print(f"  报名截止: {contest.registration_end}")
                print(f"  比赛时间: {contest.contest_start} ~ {contest.contest_end}")

                if contest.brief_description:
                    print(f"\n  简洁说明:\n{contest.brief_description}")
                if contest.eligibility_requirements:
                    print(f"\n  参赛资格:\n{contest.eligibility_requirements}")
                if contest.participation_process:
                    print(f"\n  参赛流程:\n{contest.participation_process}")
                if contest.awards_info:
                    print(f"\n  奖项信息:\n{contest.awards_info}")
                if contest.contact_info:
                    print(f"\n  联系方式:\n{contest.contact_info}")
                if contest.recommendations:
                    print(f"\n  推荐建议:\n{contest.recommendations}")

                print(f"\n  状态: {contest.status}")
            else:
                print(f"\n  状态: 待AI处理")

    finally:
        db.close()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    show_data()
