"""
测试单个页面的爬取和处理
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import YsuContestCrawler, ContestAIProcessor


def test_single_page():
    print("=" * 60)
    print("测试单页面爬取")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 步骤1: 爬取列表页，获取第一个链接
        print("\n[1/4] 爬取列表页...")
        crawler = YsuContestCrawler(db)
        try:
            links = crawler.crawl_list_page()
            if not links:
                print("没有找到链接")
                return

            print(f"找到 {len(links)} 个链接")
            first_link = links[0]
            print(f"第一个: {first_link['title']}")
            print(f"URL: {first_link['url']}")
            if first_link.get('date'):
                print(f"日期: {first_link['date']}")

            # 步骤2: 爬取详情页
            print("\n[2/4] 爬取详情页...")
            detail = crawler.crawl_detail_page(first_link['url'])
            if not detail:
                print("详情页爬取失败")
                return

            print(f"标题: {detail['title'][:50]}...")
            print(f"内容长度: {len(detail['content'])} 字符")
            if len(detail['content']) > 200:
                print(f"内容预览:\n{detail['content'][:200]}...")

            # 步骤3: 保存到数据库
            print("\n[3/4] 保存到数据库...")
            contest = crawler.save_contest(detail)
            print(f"已保存，ID: {contest.id}")
            print(f"标题: {contest.title}")

        finally:
            crawler.close()

        # 步骤4: AI处理
        print("\n[4/4] AI智能处理...")
        processor = ContestAIProcessor(db, use_llm=True)
        try:
            contest = processor.process_contest(contest.id)
            if contest:
                print(f"\nAI处理完成!")
                print(f"摘要: {contest.summary}")
                print(f"级别: {contest.level}")
                print(f"分类: {contest.category}")
                print(f"标签: {contest.tags}")
                print(f"主办方: {contest.organizer}")
                print(f"报名开始: {contest.registration_start}")
                print(f"报名截止: {contest.registration_end}")
                print(f"比赛开始: {contest.contest_start}")
                print(f"比赛结束: {contest.contest_end}")
                print(f"AI处理状态: {contest.is_ai_processed}")

        finally:
            processor.close()

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        print("\n现在可以查看数据库中的数据")
        print("或者启动后端查看:")
        print("  uv run uvicorn campus_ai.main:app --reload")

    finally:
        db.close()


if __name__ == "__main__":
    test_single_page()
