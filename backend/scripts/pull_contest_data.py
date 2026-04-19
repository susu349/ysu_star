"""
拉取赛事数据脚本 - 爬虫 + AI处理
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.core.config import get_settings
from campus_ai.services.contest import (
    YsuContestCrawler,
    ContestAIProcessor,
    init_static_contest_data,
)


def pull_and_process(max_pages: int = 10, use_llm: bool = True):
    """拉取并处理赛事数据"""
    settings = get_settings()

    # 设置DeepSeek API Key
    if use_llm and not settings.LLM_API_KEY:
        print("请先设置 LLM_API_KEY")
        use_llm = False

    db = SessionLocal()
    try:
        print("=" * 60)
        print("步骤 1: 爬取官网数据")
        print("=" * 60)

        crawler = YsuContestCrawler(db)
        try:
            contests = crawler.run_full_crawl(max_pages=max_pages)
            print(f"\n成功爬取 {len(contests)} 个赛事")

            if not contests:
                print("\n没有爬取到数据，使用静态假数据...")
                init_static_contest_data(db)
                contests = db.execute(
                    "SELECT id FROM contests LIMIT 8"
                ).fetchall()
                contests = [c[0] for c in contests] if contests else []

        finally:
            crawler.close()

        if use_llm:
            print("\n" + "=" * 60)
            print("步骤 2: AI智能处理（DeepSeek）")
            print("=" * 60)

            processor = ContestAIProcessor(db, use_llm=True)
            try:
                processed = processor.batch_process_contests(limit=len(contests) or 10)
                print(f"\n成功AI处理 {processed} 个赛事")
            finally:
                processor.close()

        print("\n" + "=" * 60)
        print("完成！")
        print("=" * 60)
        print("\n现在可以启动后端查看数据：")
        print("  uvicorn campus_ai.main:app --reload")
        print("\n访问 http://localhost:8000/docs 测试API")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="拉取赛事数据")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="最大爬取页数"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="不使用LLM，只用规则提取"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="DeepSeek API Key"
    )

    args = parser.parse_args()

    # 设置API Key
    if args.api_key:
        from campus_ai.core.config import Settings
        Settings.LLM_API_KEY = args.api_key
        os.environ["LLM_API_KEY"] = args.api_key

    pull_and_process(
        max_pages=args.max_pages,
        use_llm=not args.no_llm
    )
