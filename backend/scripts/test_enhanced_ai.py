"""测试增强版AI处理"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import ContestAIProcessor, YsuContestCrawler
from campus_ai.models import Contest


def test_enhanced_ai():
    """测试增强版AI处理"""
    print("=" * 80)
    print("测试增强版AI处理")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 找一个赛事
        contest = db.query(Contest).first()
        if not contest:
            print("没有赛事，先爬一个...")
            crawler = YsuContestCrawler(db)
            links = crawler.crawl_list_page()
            if links:
                detail = crawler.crawl_detail_page(links[0]["url"])
                if detail:
                    contest = crawler.save_contest(detail, download_attachments=True)
            crawler.close()

        if not contest:
            print("没有找到赛事")
            return

        print(f"\n赛事: {contest.title[:60]}")
        print(f"ID: {contest.id}")

        # 重置AI处理状态
        contest.is_ai_processed = False
        contest.needs_review = True
        contest.status = "draft"
        db.commit()

        # AI处理
        print("\n开始AI处理...")
        processor = ContestAIProcessor(db, use_llm=True)
        result = processor.process_contest(contest.id)

        if result:
            print("\n" + "=" * 80)
            print("AI处理结果")
            print("=" * 80)

            print(f"\n【基础信息】")
            print(f"摘要: {result.summary}")
            print(f"级别: {result.level}")
            print(f"分类: {result.category}")
            print(f"标签: {result.tags}")
            print(f"主办方: {result.organizer}")

            print(f"\n【时间信息】")
            print(f"报名开始: {result.registration_start}")
            print(f"报名截止: {result.registration_end}")
            print(f"比赛开始: {result.contest_start}")
            print(f"比赛结束: {result.contest_end}")

            print(f"\n【详细信息】")
            if result.brief_description:
                print(f"简洁说明:\n{result.brief_description}")
            if result.eligibility_requirements:
                print(f"\n参赛资格:\n{result.eligibility_requirements}")
            if result.participation_process:
                print(f"\n参赛流程:\n{result.participation_process}")
            if result.awards_info:
                print(f"\n奖项信息:\n{result.awards_info}")
            if result.contact_info:
                print(f"\n联系方式:\n{result.contact_info}")
            if result.recommendations:
                print(f"\n推荐建议:\n{result.recommendations}")

            print(f"\n【状态】")
            print(f"is_ai_processed: {result.is_ai_processed}")
            print(f"needs_review: {result.needs_review}")
            print(f"status: {result.status}")

        processor.close()

    finally:
        db.close()


if __name__ == "__main__":
    test_enhanced_ai()
