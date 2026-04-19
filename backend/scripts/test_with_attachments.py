"""
测试完整的爬取+附件下载+AI处理流程
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import (
    YsuContestCrawler,
    ContestAIProcessor,
    AttachmentService,
)


def test_full_workflow():
    print("=" * 60)
    print("测试完整流程：爬取 + 附件 + AI处理")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 步骤1: 爬取列表页，获取第一个有附件的链接
        print("\n[1/5] 爬取列表页，查找有附件的通知...")
        crawler = YsuContestCrawler(db)
        try:
            links = crawler.crawl_list_page()
            print(f"发现 {len(links)} 个链接")

            # 先爬取几个，看看哪个有附件
            target_link = None
            for link in links[:5]:
                print(f"\n检查: {link['title'][:40]}...")
                detail = crawler.crawl_detail_page(link["url"])
                if detail and detail.get("attachments"):
                    print(f"  -> 发现 {len(detail['attachments'])} 个附件!")
                    target_link = link
                    break

            if not target_link:
                print("\n没找到带附件的通知，用第一个测试")
                target_link = links[0] if links else None
                if not target_link:
                    print("没有找到任何链接")
                    return

            print(f"\n选中: {target_link['title']}")

        finally:
            crawler.close()

        # 步骤2: 爬取详情页（这次用正式爬虫，保存到数据库）
        print("\n[2/5] 爬取详情页并保存到数据库...")
        crawler = YsuContestCrawler(db)
        try:
            detail = crawler.crawl_detail_page(target_link["url"])
            if not detail:
                print("爬取详情页失败")
                return

            print(f"标题: {detail['title']}")
            print(f"内容长度: {len(detail.get('content', ''))}")
            if detail.get("attachments"):
                print(f"附件数量: {len(detail['attachments'])}")
                for att in detail["attachments"]:
                    print(f"  - {att['name']}")
                    print(f"    {att['url']}")

            contest = crawler.save_contest(detail, download_attachments=True)
            print(f"\n已保存到数据库，ID: {contest.id}")

        finally:
            crawler.close()

        # 步骤3: 检查附件
        print("\n[3/5] 检查附件...")
        att_service = AttachmentService(db)
        attachments = att_service.get_attachments_by_contest(contest.id)
        print(f"找到 {len(attachments)} 个附件记录")
        for att in attachments:
            print(f"  - {att.name}")
            print(f"    已下载: {att.is_downloaded}")
            if att.is_downloaded:
                print(f"    本地路径: {att.file_path}")
                print(f"    文件大小: {att.file_size} 字节")
                print(f"    已解析: {att.is_parsed}")

        # 步骤4: 解析附件
        if attachments:
            print("\n[4/5] 解析附件...")
            for att in attachments:
                if att.is_downloaded and not att.is_parsed:
                    print(f"解析: {att.name}")
                    content = att_service.parse_attachment(att)
                    if content:
                        print(f"  解析成功，长度: {len(content)}")
                        if len(content) > 200:
                            print(f"  预览: {content[:200]}...")

        # 步骤5: AI处理
        print("\n[5/5] AI智能处理...")
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

    finally:
        db.close()


if __name__ == "__main__":
    test_full_workflow()
