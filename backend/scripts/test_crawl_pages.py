"""测试爬取多页"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import time

from campus_ai.services.contest import YsuContestCrawler
from campus_ai.core.database import SessionLocal


def test_crawl_pages():
    """测试爬取多页"""
    db = SessionLocal()
    crawler = YsuContestCrawler(db)

    try:
        print("=" * 70)
        print("测试爬取3页列表页")
        print("=" * 70)

        all_links = []
        visited_urls = set()

        # 第1页
        print("\n--- 第1页 ---")
        links1 = crawler.crawl_list_page()
        print(f"找到 {len(links1)} 个链接")
        for link in links1:
            print(f"  - {link['title'][:50]}")
            if link["url"] not in visited_urls:
                all_links.append(link)
                visited_urls.add(link["url"])

        # 获取分页URL
        html = crawler.crawler.fetch(crawler.LIST_URL)
        soup = crawler.crawler.parse_html(html)
        page_urls = crawler._extract_pagination(soup, crawler.LIST_URL)
        print(f"\n分页URL列表 (前5个):")
        for i, url in enumerate(page_urls[:5]):
            print(f"  {i+1}. {url}")

        # 第2页
        if len(page_urls) > 1:
            print(f"\n--- 第2页: {page_urls[1]} ---")
            links2 = crawler.crawl_list_page(page_urls[1])
            print(f"找到 {len(links2)} 个链接")
            for link in links2:
                print(f"  - {link['title'][:50]}")
                if link["url"] not in visited_urls:
                    all_links.append(link)
                    visited_urls.add(link["url"])
            time.sleep(0.5)

        # 第3页
        if len(page_urls) > 2:
            print(f"\n--- 第3页: {page_urls[2]} ---")
            links3 = crawler.crawl_list_page(page_urls[2])
            print(f"找到 {len(links3)} 个链接")
            for link in links3:
                print(f"  - {link['title'][:50]}")
                if link["url"] not in visited_urls:
                    all_links.append(link)
                    visited_urls.add(link["url"])

        print(f"\n总共发现 {len(all_links)} 个不重复的链接")

    finally:
        crawler.close()
        db.close()


if __name__ == "__main__":
    test_crawl_pages()
