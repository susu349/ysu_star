"""
完整的赛事数据爬取脚本 - 支持全量/增量，可定时运行
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import time
import argparse
from datetime import datetime

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import (
    YsuContestCrawler,
    ContestAIProcessor,
)


def crawl_all(db, max_list_pages: int = 10, max_detail_pages: int = None, skip_ai: bool = False):
    """爬取所有赛事"""
    print("=" * 70)
    print(f"赛事数据爬取 - 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

    # 限制处理数量
    if max_detail_pages:
        new_links = new_links[:max_detail_pages]
        print(f"\n限制处理前 {max_detail_pages} 个")

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
                # 回滚事务
                try:
                    db.rollback()
                except:
                    pass

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="爬取赛事数据")
    parser.add_argument(
        "--list-pages",
        type=int,
        default=5,
        help="最多爬取多少页列表页 (默认: 5)"
    )
    parser.add_argument(
        "--detail-pages",
        type=int,
        default=None,
        help="最多处理多少个详情页 (默认: 不限制)"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="跳过AI处理"
    )

    args = parser.parse_args()

    db = SessionLocal()
    try:
        crawl_all(db, max_list_pages=args.list_pages, max_detail_pages=args.detail_pages, skip_ai=args.skip_ai)
    finally:
        db.close()
