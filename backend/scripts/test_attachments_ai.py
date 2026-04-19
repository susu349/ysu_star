"""测试附件解析和AI处理"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import ContestAIProcessor, YsuContestCrawler
from campus_ai.services.contest.attachment_service import AttachmentService
from campus_ai.models import Contest


def test_attachment_parsing():
    """测试附件解析"""
    print("=" * 70)
    print("测试附件解析和AI处理")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 找一个有附件的赛事
        contest = db.query(Contest).filter(Contest.source_url != None).first()
        if not contest:
            print("没有找到赛事，先爬一个...")
            crawler = YsuContestCrawler(db)
            links = crawler.crawl_list_page()
            if links:
                detail = crawler.crawl_detail_page(links[0]["url"])
                if detail:
                    contest = crawler.save_contest(detail, download_attachments=True)
                    print(f"已创建赛事: {contest.title}")
            crawler.close()

        if not contest:
            print("没有找到赛事")
            return

        print(f"\n赛事: {contest.title}")
        print(f"ID: {contest.id}")

        # 测试附件解析
        att_service = AttachmentService(db)
        attachments = att_service.get_attachments_by_contest(contest.id)
        print(f"\n找到 {len(attachments)} 个附件:")

        for att in attachments:
            print(f"\n  - {att.name}")
            print(f"    类型: {att.file_type}")
            print(f"    已下载: {att.is_downloaded}")
            print(f"    已解析: {att.is_parsed}")

            if att.is_downloaded and not att.is_parsed:
                print(f"    正在解析...")
                content = att_service.parse_attachment(att)
                if content:
                    print(f"    解析成功，长度: {len(content)}")
                    print(f"    预览: {content[:200]}...")
                else:
                    print(f"    解析失败")
            elif att.is_parsed:
                print(f"    内容长度: {len(att.parsed_content or '')}")
                print(f"    预览: {att.parsed_content[:200]}...")

        # 测试AI处理（包含附件内容）
        print(f"\n" + "=" * 70)
        print("测试AI处理（包含附件内容）")
        print("=" * 70)

        processor = ContestAIProcessor(db, use_llm=True)
        processor._get_attachment_contents(contest)
        result = processor.process_contest(contest.id)

        if result:
            print(f"\nAI处理完成:")
            print(f"  摘要: {result.summary}")
            print(f"  级别: {result.level}")
            print(f"  分类: {result.category}")
            print(f"  标签: {result.tags}")
            print(f"  主办方: {result.organizer}")
            print(f"  报名截止: {result.registration_end}")
            print(f"  比赛时间: {result.contest_start} ~ {result.contest_end}")

        processor.close()

    finally:
        db.close()


if __name__ == "__main__":
    test_attachment_parsing()
