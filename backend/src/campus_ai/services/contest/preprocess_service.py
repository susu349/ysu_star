"""
赛事文档预处理服务 - 从原始内容提取结构化信息
"""
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


class ContestPreprocessor:
    """赛事内容预处理器"""

    def __init__(self):
        # 常见日期格式正则
        self.date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?',
            r'报名截止[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'截止时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]

        # 级别关键词
        self.level_keywords = {
            "国际": ["国际", "全球", "world", "international"],
            "国赛": ["全国", "国家", "national", "china"],
            "省赛": ["河北省", "省级", "province"],
            "校赛": ["燕山大学", "校", "校内", "school"],
        }

        # 分类关键词
        self.category_keywords = {
            "科技创新": ["挑战杯", "创新", "科技", "发明"],
            "创新创业": ["互联网+", "创业", "商业"],
            "程序设计": ["ACM", "程序设计", "编程", "算法", "代码"],
            "数学建模": ["数学建模", "数模", "建模"],
            "电子设计": ["电子设计", "嵌入式", "硬件", "电路"],
            "机械设计": ["机械", "结构", "三维", "SolidWorks"],
            "计算机设计": ["计设赛", "软件设计", "数字媒体"],
            "节能减排": ["节能", "减排", "环保", "绿色"],
        }

    def extract_dates(self, text: str) -> Dict[str, Optional[datetime]]:
        """从文本中提取日期"""
        dates = {
            "registration_start": None,
            "registration_end": None,
            "contest_start": None,
            "contest_end": None,
        }

        lines = text.split('\n')
        for line in lines:
            line = line.strip()

            # 报名截止
            if any(keyword in line for keyword in ["报名截止", "截止报名"]):
                date = self._extract_single_date(line)
                if date:
                    dates["registration_end"] = date

            # 比赛开始
            elif any(keyword in line for keyword in ["比赛时间", "竞赛时间", "举办时间"]):
                date = self._extract_single_date(line)
                if date:
                    dates["contest_start"] = date

        return dates

    def _extract_single_date(self, text: str) -> Optional[datetime]:
        """提取单个日期"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year, month, day = map(int, match.groups())
                    return datetime(year, month, day)
                except (ValueError, TypeError):
                    continue
        return None

    def extract_level(self, text: str, title: str = "") -> str:
        """提取赛事级别"""
        combined = (title + " " + text).lower()

        from ...models import ContestLevel

        levels = [
            (ContestLevel.INTERNATIONAL, self.level_keywords["国际"]),
            (ContestLevel.NATIONAL, self.level_keywords["国赛"]),
            (ContestLevel.PROVINCE, self.level_keywords["省赛"]),
            (ContestLevel.SCHOOL, self.level_keywords["校赛"]),
        ]

        for level, keywords in levels:
            if any(kw in combined for kw in keywords):
                return level

        return ContestLevel.SCHOOL

    def extract_category(self, text: str, title: str = "") -> str:
        """提取赛事分类"""
        combined = (title + " " + text)

        for category, keywords in self.category_keywords.items():
            if any(kw in combined for kw in keywords):
                return category

        return "其他"

    def extract_tags(self, text: str, title: str = "") -> List[str]:
        """提取标签"""
        combined = (title + " " + text)
        tags = []

        for category, keywords in self.category_keywords.items():
            for kw in keywords:
                if kw in combined and kw not in tags:
                    tags.append(kw)

        return tags[:5]  # 最多5个标签

    def extract_summary(self, text: str, max_length: int = 100) -> str:
        """提取100字以内的摘要"""
        # 先尝试找报名截止、参赛对象等关键信息
        key_lines = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ["报名", "参赛", "对象", "时间", "级别"]):
                if len(line) > 5:
                    key_lines.append(line)

        if key_lines:
            summary = "，".join(key_lines[:2])
        else:
            # 如果没找到关键行，取前几句
            sentences = self._split_sentences(text)
            summary = "".join(sentences[:2])

        # 截断到max_length
        if len(summary) > max_length:
            summary = summary[:max_length-1] + "…"

        return summary

    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        import re
        sentences = re.split(r'([。！？.!?])', text)
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if sentences[i]:
                result.append(sentences[i] + sentences[i + 1])
        if len(sentences) % 2 == 1 and sentences[-1]:
            result.append(sentences[-1])
        return result

    def extract_organizer(self, text: str) -> Optional[str]:
        """提取主办方"""
        patterns = [
            r'主办[单位方][：:]\s*([^\n]+)',
            r'承办[单位方][：:]\s*([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def preprocess_contest(
        self,
        title: str,
        content: str,
    ) -> Dict[str, Any]:
        """预处理赛事内容，提取结构化信息"""
        dates = self.extract_dates(content)

        return {
            "title": title,
            "summary": self.extract_summary(content),
            "level": self.extract_level(content, title),
            "category": self.extract_category(content, title),
            "tags": self.extract_tags(content, title),
            "organizer": self.extract_organizer(content),
            "registration_start": dates["registration_start"],
            "registration_end": dates["registration_end"],
            "contest_start": dates["contest_start"],
            "contest_end": dates["contest_end"],
            "is_ai_processed": True,
            "needs_review": False,
        }
