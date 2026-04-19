"""批量处理未AI处理的赛事"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.database import SessionLocal
from campus_ai.services.contest import ContestAIProcessor
from campus_ai.models import Contest


def batch_process(limit: int = None):
    """批量处理"""
    print("=" * 80)
    print("批量AI处理赛事")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 统计
        total = db.query(Contest).count()
        processed = db.query(Contest).filter(Contest.is_ai_processed == True).count()
        unprocessed = db.query(Contest).filter(Contest.is_ai_processed == False).count()

        print(f"\n统计:")
        print(f"  总赛事: {total}")
        print(f"  已AI处理: {processed}")
        print(f"  未处理: {unprocessed}")

        # 获取未处理的
        query = db.query(Contest).filter(Contest.is_ai_processed == False)
        if limit:
            query = query.limit(limit)

        contests = query.all()
        print(f"\n准备处理 {len(contests)} 个赛事")

        processor = ContestAIProcessor(db, use_llm=True)

        success_count = 0
        fail_count = 0

        for i, contest in enumerate(contests, 1):
            print(f"\n[{i}/{len(contests)}] {contest.title[:50]}")
            try:
                result = processor.process_contest(contest.id)
                if result and result.is_ai_processed:
                    print(f"  ✓ 成功")
                    success_count += 1
                else:
                    print(f"  ✗ 未标记为已处理")
                    fail_count += 1
            except Exception as e:
                print(f"  ✗ 失败: {e}")
                fail_count += 1
                # 回滚
                try:
                    db.rollback()
                except:
                    pass

        processor.close()

        print(f"\n" + "=" * 80)
        print(f"处理完成!")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="批量AI处理")
    parser.add_argument("--limit", type=int, default=None, help="处理数量限制")
    args = parser.parse_args()

    batch_process(limit=args.limit)
