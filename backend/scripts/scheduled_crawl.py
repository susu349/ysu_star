"""
定时爬取脚本 - 用于每天自动增量更新赛事数据

使用方式:
    # 立即运行一次全量爬取
    python scripts/scheduled_crawl.py --full

    # 每天定时运行增量爬取
    python scripts/scheduled_crawl.py --schedule

    # 定时运行并指定爬取页数
    python scripts/scheduled_crawl.py --schedule --list-pages 10
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import time
import argparse
import schedule
from datetime import datetime

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import (
    YsuContestCrawler,
    ContestAIProcessor,
)


def incremental_crawl(db, max_list_pages: int = 70, skip_ai: bool = False):
    """增量爬取：只爬取新的赛事"""
    print("=" * 70)
    print(f"增量赛事数据爬取 - 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 步骤1: 爬取列表页
    print(f"\n[1/4] 爬取列表页 (最多 {max_list_pages} 页)...")
    print("-" * 70)

    crawler = YsuContestCrawler(db)
    all_links = []
    visited_urls = set()

    try:
        # 先获取第一页并提取分页
        first_html = crawler.crawler.fetch(crawler.LIST_URL)
        if not first_html:
            print("无法获取第一页")
            return
        soup = crawler.crawler.parse_html(first_html)

        # 提取第一页链接
        links = crawler._extract_contest_links(soup, crawler.LIST_URL)
        for link in links:
            if link["url"] not in visited_urls:
                all_links.append(link)
                visited_urls.add(link["url"])
        print(f"第1页: 找到 {len(links)} 个链接 (累计: {len(all_links)})")

        # 爬取更多分页
        if max_list_pages > 1:
            page_urls = crawler._extract_pagination(soup, crawler.LIST_URL)

            for i, page_url in enumerate(page_urls[1:max_list_pages]):  # 从第2页开始
                print(f"第{i+2}页: {page_url}")
                page_links = crawler.crawl_list_page(page_url)
                for link in page_links:
                    if link["url"] not in visited_urls:
                        all_links.append(link)
                        visited_urls.add(link["url"])
                time.sleep(0.5)
                print(f"  找到 {len(page_links)} 个链接 (累计: {len(all_links)})")

    finally:
        crawler.close()

    if not all_links:
        print("\n没有找到任何链接")
        return

    print(f"\n总共发现 {len(all_links)} 个赛事链接")

    # 步骤2: 检查哪些是新的，哪些已存在
    print(f"\n[2/4] 检查现有数据...")
    print("-" * 70)

    from campus_ai.models import Contest
    existing_urls = set()
    existing_contests = db.query(Contest).all()
    for c in existing_contests:
        if c.source_url:
            existing_urls.add(c.source_url)

    new_links = [link for link in all_links if link["url"] not in existing_urls]
    print(f"已存在: {len(existing_urls)} 个")
    print(f"新发现: {len(new_links)} 个")

    if not new_links:
        print("\n没有新赛事，结束")
        return

    # 步骤3: 爬取详情页
    print(f"\n[3/4] 爬取详情页...")
    print("-" * 70)

    crawler = YsuContestCrawler(db)
    saved_contests = []

    try:
        for i, link_info in enumerate(new_links):
            url = link_info["url"]
            title = link_info["title"][:40] if len(link_info["title"]) > 40 else link_info["title"]
            print(f"[{i+1}/{len(new_links)}] {title}")

            try:
                detail = crawler.crawl_detail_page(url)
                if detail:
                    contest = crawler.save_contest(detail, download_attachments=True)
                    saved_contests.append(contest)
                    print(f"  → 已保存, ID: {contest.id}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  → 失败: {e}")

    finally:
        crawler.close()

    print(f"\n成功爬取 {len(saved_contests)} 个新赛事")

    if skip_ai:
        print("\n跳过AI处理")
        return saved_contests

    # 步骤4: AI处理
    print(f"\n[4/4] AI智能处理...")
    print("-" * 70)

    processor = ContestAIProcessor(db, use_llm=True)
    processed = 0

    try:
        for contest in saved_contests:
            print(f"处理: {contest.title[:40]}...")
            try:
                processor.process_contest(contest.id)
                processed += 1
                print(f"  → 完成")
            except Exception as e:
                print(f"  → 失败: {e}")

    finally:
        processor.close()

    print(f"\nAI处理完成 {processed} 个")
    print(f"\n" + "=" * 70)
    print(f"全部完成 - 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    return saved_contests


def job(list_pages: int = 70, skip_ai: bool = False):
    """定时任务"""
    db = SessionLocal()
    try:
        incremental_crawl(db, max_list_pages=list_pages, skip_ai=skip_ai)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="定时爬取赛事数据")
    parser.add_argument(
        "--full",
        action="store_true",
        help="立即运行一次全量爬取(70页)"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="启动定时任务，每天凌晨2点运行"
    )
    parser.add_argument(
        "--list-pages",
        type=int,
        default=70,
        help="每次爬取多少页列表页 (默认: 70)"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="跳过AI处理"
    )
    parser.add_argument(
        "--time",
        type=str,
        default="02:00",
        help="定时运行时间 (默认: 02:00)"
    )

    args = parser.parse_args()

    if args.full:
        # 立即运行一次
        print("立即运行全量爬取...")
        job(list_pages=args.list_pages, skip_ai=args.skip_ai)
    elif args.schedule:
        # 启动定时任务
        print(f"启动定时任务，每天 {args.time} 运行...")
        schedule.every().day.at(args.time).do(job, list_pages=args.list_pages, skip_ai=args.skip_ai)

        print(f"定时任务已启动，首次运行将在今天 {args.time}")
        print("按 Ctrl+C 停止...")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n定时任务已停止")
    else:
        # 默认只运行一次增量
        print("运行一次增量爬取...")
        job(list_pages=args.list_pages, skip_ai=args.skip_ai)
