"""
完整的赛事数据爬取和处理脚本
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import (
    YsuContestCrawler,
    ContestAIProcessor,
    init_static_contest_data,
)


def main():
    print("=" * 60)
    print("赛事数据爬取与处理")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 步骤1: 爬取官网数据
        print("\n[步骤 1/3] 爬取创新创业学院官网...")
        print("-" * 60)

        crawler = YsuContestCrawler(db)
        try:
            contests = crawler.run_full_crawl(max_pages=1000, max_list_pages=1000)

            if not contests:
                print("\n未爬取到数据，使用静态假数据...")
                init_static_contest_data(db)
                # 查询刚插入的静态数据
                from campus_ai.models import Contest
                contests = db.query(Contest).limit(8).all()
        finally:
            crawler.close()

        if not contests:
            print("\n没有数据可以处理")
            return

        print(f"\n成功获取 {len(contests)} 个赛事")

        # 步骤2: AI智能处理
        print("\n[步骤 2/3] AI智能提取结构化信息...")
        print("-" * 60)

        processor = ContestAIProcessor(db, use_llm=True)
        try:
            processed = 0
            for contest in contests:
                print(f"处理: {contest.title[:30]}...")
                try:
                    processor.process_contest(contest.id)
                    processed += 1
                except Exception as e:
                    print(f"  处理失败: {e}")
                    contest.needs_review = True
                    db.commit()

            print(f"\n成功AI处理 {processed} 个赛事")
        finally:
            processor.close()

        # 步骤3: 完成
        print("\n[步骤 3/3] 完成!")
        print("=" * 60)
        print("\n数据已准备就绪!")
        print("\n可以启动后端查看:")
        print("  uv run uvicorn campus_ai.main:app --reload")
        print("\n访问API文档:")
        print("  http://127.0.0.1:8000/docs")
        print("\n可用接口:")
        print("  GET  /api/v1/contest/list        - 查看赛事列表")
        print("  GET  /api/v1/contest/{id}      - 查看赛事详情")
        print("  POST /api/v1/contest/crawl       - 手动触发爬虫")
        print("  POST /api/v1/contest/process/{id} - AI处理单个赛事")

    finally:
        db.close()


if __name__ == "__main__":
    main()
