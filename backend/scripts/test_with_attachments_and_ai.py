"""测试带附件的完整流程"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import YsuContestCrawler, ContestAIProcessor
from campus_ai.services.contest.attachment_service import AttachmentService


def test_with_attachments():
    """测试带附件的爬取和AI处理"""
    print("=" * 70)
    print("测试带附件的爬取和AI处理")
    print("=" * 70)

    db = SessionLocal()
    crawler = YsuContestCrawler(db)

    try:
        # 先爬取列表页，找一个有附件的链接
        print("\n[1/4] 爬取列表页...")
        links = crawler.crawl_list_page()
        print(f"找到 {len(links)} 个链接")

        # 逐个爬取详情页，直到找到有附件的
        contest = None
        for i, link_info in enumerate(links[:5]):
            url = link_info["url"]
            print(f"\n尝试 [{i+1}]: {link_info['title'][:40]}")
            detail = crawler.crawl_detail_page(url)
            if detail and detail.get("attachments"):
                print(f"  找到 {len(detail['attachments'])} 个附件！")
                contest = crawler.save_contest(detail, download_attachments=True)
                break
            else:
                print(f"  没有附件，跳过")

        if not contest:
            print("\n没有找到带附件的赛事，用第一个测试")
            detail = crawler.crawl_detail_page(links[0]["url"])
            contest = crawler.save_contest(detail, download_attachments=True)

        print(f"\n[2/4] 赛事已保存: {contest.title[:50]}")
        print(f"    ID: {contest.id}")

        # 检查附件
        att_service = AttachmentService(db)
        attachments = att_service.get_attachments_by_contest(contest.id)
        print(f"\n[3/4] 附件情况: {len(attachments)} 个")

        for att in attachments:
            print(f"  - {att.name}")
            if att.is_downloaded and not att.is_parsed:
                print(f"    正在解析...")
                content = att_service.parse_attachment(att)
                if content:
                    print(f"    解析成功: {len(content)} 字符")
                else:
                    print(f"    解析失败")

        # AI处理（含附件）
        print(f"\n[4/4] AI处理...")
        processor = ContestAIProcessor(db, use_llm=True)
        result = processor.process_contest(contest.id)

        if result:
            print(f"\n处理完成:")
            print(f"  摘要: {result.summary}")
            print(f"  级别: {result.level}")
            print(f"  分类: {result.category}")
            print(f"  标签: {result.tags}")
            print(f"  主办方: {result.organizer}")
            print(f"  报名截止: {result.registration_end}")

        processor.close()

    finally:
        crawler.close()
        db.close()


if __name__ == "__main__":
    test_with_attachments()
