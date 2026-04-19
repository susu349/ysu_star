"""测试分页逻辑"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.services.contest import YsuContestCrawler
from campus_ai.core.database import SessionLocal


def test_pagination():
    """测试分页链接提取"""
    db = SessionLocal()
    crawler = YsuContestCrawler(db)

    try:
        print("=" * 70)
        print("测试分页逻辑")
        print("=" * 70)

        # 获取第一页HTML
        html = crawler.crawler.fetch(crawler.LIST_URL)
        if not html:
            print("无法获取第一页")
            return

        soup = crawler.crawler.parse_html(html)

        # 查找分页区域
        pagination = soup.find("div", class_="pb_sys_common")
        if pagination:
            print("\n找到分页区域:")
            print(pagination.get_text(strip=True)[:200])

            # 查找所有链接
            links = pagination.find_all("a", href=True)
            print(f"\n找到 {len(links)} 个分页链接:")
            for a in links:
                print(f"  - {a.get_text(strip=True):10} → {a['href']}")

        # 测试_extract_pagination
        page_urls = crawler._extract_pagination(soup, crawler.LIST_URL)
        print(f"\n_extract_pagination 返回 {len(page_urls)} 个URL:")
        for i, url in enumerate(page_urls[:10]):
            print(f"  {i+1}. {url}")
        if len(page_urls) > 10:
            print(f"  ... 还有 {len(page_urls) - 10} 个")

    finally:
        crawler.close()
        db.close()


if __name__ == "__main__":
    test_pagination()
