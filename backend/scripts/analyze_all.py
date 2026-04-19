"""
爬取所有页面，分析附件情况
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import YsuContestCrawler


def analyze_all():
    print("=" * 60)
    print("爬取并分析所有页面")
    print("=" * 60)

    db = SessionLocal()
    try:
        crawler = YsuContestCrawler(db)
        try:
            # 1. 爬取列表页和分页
            print("\n[1/3] 爬取列表页...")
            html = crawler.crawler.fetch(crawler.LIST_URL)
            if not html:
                print("无法获取第一页")
                return

            soup = crawler.crawler.parse_html(html)

            # 提取第一页链接
            links = crawler._extract_contest_links(soup, crawler.LIST_URL)
            print(f"第一页发现 {len(links)} 个链接")

            # 提取所有分页
            page_urls = crawler._extract_pagination(soup, crawler.LIST_URL)
            print(f"发现 {len(page_urls)} 个分页")

            # 爬取所有分页获取所有链接
            all_links = links.copy()
            visited_urls = set([l["url"] for l in links])

            for i, page_url in enumerate(page_urls):
                print(f"\n爬取分页 [{i+2}/{len(page_urls)+1}]: {page_url}")
                page_links = crawler.crawl_list_page(page_url)
                for link in page_links:
                    if link["url"] not in visited_urls:
                        all_links.append(link)
                        visited_urls.add(link["url"])

            print(f"\n总共发现 {len(all_links)} 个赛事链接")

            # 2. 爬取每个详情页，分析附件
            print("\n[2/3] 爬取详情页并分析附件...")
            print("-" * 60)

            all_attachments = []
            attachment_types = {}

            for i, link_info in enumerate(all_links):
                url = link_info["url"]
                title = link_info["title"][:40] if len(link_info["title"]) > 40 else link_info["title"]
                print(f"[{i+1}/{len(all_links)}] {title}")

                try:
                    detail = crawler.crawl_detail_page(url)
                    if detail and detail.get("attachments"):
                        attachments = detail["attachments"]
                        print(f"  -> 发现 {len(attachments)} 个附件")

                        for att in attachments:
                            att_url = att["url"]
                            att_name = att["name"]

                            # 提取文件扩展名
                            ext = os.path.splitext(att_url.split("?")[0])[1].lower()
                            if not ext:
                                # 从文件名尝试提取
                                ext = os.path.splitext(att_name.split("?")[0])[1].lower()

                            if ext:
                                if ext not in attachment_types:
                                    attachment_types[ext] = 0
                                attachment_types[ext] += 1

                            all_attachments.append({
                                "title": title,
                                "name": att_name,
                                "url": att_url,
                                "ext": ext,
                            })

                except Exception as e:
                    print(f"  -> 爬取失败: {e}")

                import time
                time.sleep(0.5)  # 慢点爬

            # 3. 输出分析结果
            print("\n[3/3] 分析结果")
            print("=" * 60)
            print(f"\n总共发现 {len(all_attachments)} 个附件")
            print(f"\n附件类型统计:")
            for ext, count in sorted(attachment_types.items(), key=lambda x: -x[1]):
                print(f"  {ext or '无后缀'}: {count} 个")

            if all_attachments:
                print(f"\n附件列表 (前20个):")
                for i, att in enumerate(all_attachments[:20]):
                    print(f"  [{i+1}] {att['name']}")
                    print(f"       {att['url']}")

            print("\n" + "=" * 60)
            print("分析完成!")

        finally:
            crawler.close()

    finally:
        db.close()


if __name__ == "__main__":
    analyze_all()
