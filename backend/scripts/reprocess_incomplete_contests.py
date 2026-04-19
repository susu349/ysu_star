#!/usr/bin/env python3
"""重新处理标记为已AI处理但缺少详细信息的赛事"""
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from campus_ai.core.config import get_settings
from campus_ai.models import Contest
from campus_ai.services.contest.preprocess_service import ContestPreprocessor


class ImprovedContestPreprocessor(ContestPreprocessor):
    """改进的预处理器，增加详细信息提取"""

    def extract_brief_description(self, text: str) -> str:
        """提取简洁说明 - 200字左右"""
        sentences = self._split_sentences(text)
        # 优先选择包含关键信息的句子
        key_sentences = []
        for s in sentences:
            if any(kw in s for kw in ['大赛', '竞赛', '举办', '参赛', '报名', '作品', '设计']):
                if len(s.strip()) > 10:
                    key_sentences.append(s.strip())

        if key_sentences:
            desc = ''.join(key_sentences[:3])
        else:
            desc = ''.join(sentences[:3])

        if len(desc) > 250:
            desc = desc[:247] + '…'
        return desc

    def extract_eligibility(self, text: str) -> str:
        """提取参赛资格"""
        lines = text.split('\n')
        eligibility_lines = []
        in_section = False

        for line in lines:
            line = line.strip()
            if any(kw in line for kw in ['参赛对象', '参赛要求', '参赛资格', '报名条件']):
                in_section = True
                eligibility_lines.append(line)
            elif in_section and line and (line.startswith('一、') or line.startswith('二、') or line.startswith('三、') or line.startswith('1、') or line.startswith('2、')):
                    if any(kw in line for kw in ['赛项', '时间', '方式']):
                        break
                    eligibility_lines.append(line)
            elif in_section and line:
                eligibility_lines.append(line)

        if eligibility_lines:
            return '\n'.join(eligibility_lines[:8])
        return None

    def extract_participation_process(self, text: str) -> str:
        """提取参赛流程"""
        lines = text.split('\n')
        process_lines = []
        in_section = False

        for line in lines:
            line = line.strip()
            if any(kw in line for kw in ['参赛方式', '报名方式', '提交方式', '参赛流程', '报名流程']):
                in_section = True
                process_lines.append(line)
            elif in_section and line and (line.startswith('一、') or line.startswith('二、') or line.startswith('三、')):
                    if any(kw in line for kw in ['赛项', '对象', '奖项', '时间']):
                        break
                    process_lines.append(line)
            elif in_section and line:
                process_lines.append(line)

        if process_lines:
            return '\n'.join(process_lines[:10])
        return None

    def extract_awards_info(self, text: str) -> str:
        """提取奖项信息"""
        lines = text.split('\n')
        awards_lines = []
        in_section = False

        for line in lines:
            line = line.strip()
            if any(kw in line for kw in ['奖项', '奖励', '评奖', '获奖', '学分']):
                in_section = True
                awards_lines.append(line)
            elif in_section and line and (line.startswith('一、') or line.startswith('二、') or line.startswith('三、')):
                if any(kw in line for kw in ['赛项', '对象', '方式', '时间']):
                    break
                awards_lines.append(line)
            elif in_section and line:
                awards_lines.append(line)

        if awards_lines:
            return '\n'.join(awards_lines[:10])
        return None

    def extract_recommendations(self, text: str) -> str:
        """提取推荐建议"""
        # 基于内容生成简单建议
        recommendations = []

        if '三维' in text or '设计' in text:
            recommendations.append('建议有三维建模基础的同学参加')
        if '团队' in text:
            recommendations.append('建议组建跨专业团队，优势互补')
        if '指导教师' in text:
            recommendations.append('提前联系指导老师获得专业指导')

        if recommendations:
            return '\n'.join(recommendations)
        return None

    def preprocess_contest(self, title: str, content: str):
        """预处理赛事内容，提取结构化信息"""
        result = super().preprocess_contest(title, content)

        # 添加详细信息字段
        result['brief_description'] = self.extract_brief_description(content)
        result['eligibility_requirements'] = self.extract_eligibility(content)
        result['participation_process'] = self.extract_participation_process(content)
        result['awards_info'] = self.extract_awards_info(content)
        result['recommendations'] = self.extract_recommendations(content)

        return result


def update_contest_from_dict(contest: Contest, data: dict):
    """从字典更新赛事"""
    # 基础字段
    fields = [
        "summary", "level", "category", "tags", "organizer",
        "registration_start", "registration_end",
        "contest_start", "contest_end",
    ]
    for field in fields:
        if field in data and data[field] is not None:
            setattr(contest, field, data[field])

    # 详细信息字段
    detail_fields = [
        "brief_description",
        "eligibility_requirements",
        "participation_process",
        "awards_info",
        "recommendations",
    ]
    for field in detail_fields:
        if field in data and data[field] is not None:
            setattr(contest, field, data[field])


def main():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    preprocessor = ImprovedContestPreprocessor()

    try:
        # 找出需要重新处理的赛事
        contests = db.query(Contest).filter(
            Contest.is_ai_processed == True,
            (Contest.brief_description == None) |
            (Contest.eligibility_requirements == None) |
            (Contest.participation_process == None) |
            (Contest.awards_info == None) |
            (Contest.recommendations == None)
        ).all()

        print(f"找到 {len(contests)} 个需要重新处理的赛事")

        updated_count = 0
        for contest in contests:
            content = contest.raw_content or contest.description or ""
            if content:
                extracted = preprocessor.preprocess_contest(contest.title or "", content)
                update_contest_from_dict(contest, extracted)
                contest.is_ai_processed = True
                updated_count += 1
                print(f"  已处理: {contest.title[:50]}...")

        db.commit()
        print(f"\n已更新 {updated_count} 个赛事")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
