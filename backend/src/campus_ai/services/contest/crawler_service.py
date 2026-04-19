"""
赛事爬虫服务 - 针对创新创业学院官网
"""
import re
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from sqlalchemy.orm import Session

from ...core.utils.crawler_base import BaseCrawler, normalize_url
from ...models import Contest, ContestLevel, ContestStatus
from ...core.config import get_settings
from .attachment_service import create_contest_attachments

settings = get_settings()


class YsuContestCrawler:
    """燕山大学创新创业学院赛事爬虫"""

    BASE_URL = "https://cxcy.ysu.edu.cn"
    LIST_URL = "https://cxcy.ysu.edu.cn/index/shou/tzgg.htm"

    def __init__(self, db: Session):
        self.db = db
        self.crawler = BaseCrawler(self.BASE_URL)

    def crawl_list_page(self, url: str = None) -> List[Dict[str, Any]]:
        """爬取列表页，获取所有赛事链接"""
        url = url or self.LIST_URL
        html = self.crawler.fetch(url)
        if not html:
            return []

        soup = self.crawler.parse_html(html)
        links = self._extract_contest_links(soup, url)
        return links

    def _extract_contest_links(self, soup, base_url: str) -> List[Dict[str, Any]]:
        """从列表页提取赛事链接"""
        contests = []

        # 针对燕山大学双创学院网站的结构
        # 每个通知在 div.font-list 里
        for item in soup.find_all("div", class_="font-list"):
            a_tag = item.find("a", class_="font-link", href=True)
            if not a_tag:
                continue

            href = a_tag["href"]
            title = a_tag.get_text(strip=True)

            if not title or len(title) < 2:
                continue

            full_url = urljoin(base_url, href)

            # 只保留同域名链接，且是info详情页
            if urlparse(full_url).netloc != urlparse(self.BASE_URL).netloc:
                continue
            if "/info/" not in full_url:
                continue

            # 提取日期
            date_str = None
            date_span = item.find("span")
            if date_span:
                date_text = date_span.get_text(strip=True)
                # 匹配 2026-04-17 格式
                date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
                if date_match:
                    try:
                        year, month, day = map(int, date_match.groups())
                        date_str = datetime(year, month, day)
                    except (ValueError, TypeError):
                        pass

            contests.append({
                "title": title,
                "url": normalize_url(full_url),
                "date": date_str,
            })

        return contests

    def _extract_main_content(self, soup) -> Optional[str]:
        """尝试提取主要内容区域"""
        # 针对燕山大学双创学院网站的选择器
        selectors = [
            "div.v_news_content",  # 实测这个是正文区域
            "div.content",
            "div.main",
            "div.article",
            "div.news-detail",
            "div.news-content",
            "#content",
            "#main",
            ".article-content",
            ".news-article",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # 移除不需要的元素
                for unwanted in element(["script", "style", "nav", "footer", "aside"]):
                    unwanted.decompose()
                text = element.get_text(separator="\n", strip=True)
                if text and len(text) > 50:
                    return text

        return None

    def _extract_attachments(self, soup, base_url: str) -> List[Dict[str, str]]:
        """提取附件链接"""
        attachments = []
        # 常见附件后缀
        ext_list = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar"]

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True)

            # 检查链接或文本中是否包含附件后缀
            has_attachment = any(ext in href.lower() or ext in text.lower() for ext in ext_list)
            if has_attachment:
                full_url = urljoin(base_url, href)
                attachments.append({
                    "name": text or "附件",
                    "url": full_url,
                })

        return attachments

    def crawl_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        """爬取详情页，获取完整赛事信息"""
        html = self.crawler.fetch(url)
        if not html:
            return None

        soup = self.crawler.parse_html(html)

        title = self.crawler.extract_title(soup)
        content = self.crawler.extract_text(soup)

        # 尝试提取正文内容区域
        main_content = self._extract_main_content(soup)
        if main_content:
            content = main_content

        # 提取附件
        attachments = self._extract_attachments(soup, url)

        return {
            "title": title,
            "content": content,
            "attachments": attachments,
            "url": url,
        }

    def save_contest(self, data: Dict[str, Any], download_attachments: bool = False) -> Contest:
        """保存赛事到数据库"""
        # 检查是否已存在
        existing = self.db.query(Contest).filter(
            Contest.source_url == data["url"]
        ).first()

        # 处理附件信息
        attachments = data.get("attachments", [])
        description_extra = ""
        if attachments:
            # 把附件信息也加到description里方便查看
            description_extra = "\n\n【附件】\n" + "\n".join([
                f"- {a['name']}: {a['url']}"
                for a in attachments
            ])

        if existing:
            # 更新现有记录
            existing.title = data.get("title", existing.title)
            existing.raw_content = data.get("content")
            existing.description = (existing.description or "") + description_extra
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            contest = existing
        else:
            # 创建新记录 - 注意：source_file 不再存JSON，附件用 ContestAttachment 表
            contest = Contest(
                id=str(uuid.uuid4()),
                title=data.get("title", "未命名赛事"),
                raw_content=data.get("content"),
                description=description_extra if description_extra else None,
                source_url=data.get("url"),
                source="crawler",
                level=ContestLevel.SCHOOL,  # 默认校赛
                category="科技创新",  # 默认分类
                status=ContestStatus.DRAFT,
                is_ai_processed=False,
                needs_review=True,
            )
            self.db.add(contest)
            self.db.commit()
            self.db.refresh(contest)

        # 处理附件
        if attachments:
            create_contest_attachments(self.db, contest, attachments, download=download_attachments)

        return contest

    def _extract_pagination(self, soup, base_url: str) -> List[str]:
        """提取分页链接 - 燕山大学网站有70页"""
        page_urls = []

        # 查找分页区域，先从尾页链接获取正确的数字
        pagination = soup.find("div", class_="pb_sys_common")
        total_pages = 70  # 默认70页

        if pagination:
            # 从下页链接获取：下一页是第2页，URL是 tzgg/69.htm
            # 所以总页数 = 69 + 1 = 70
            next_link = pagination.find("a", string="下页")
            if next_link and next_link.get("href"):
                href = next_link["href"]
                match = re.search(r"tzgg/(\d+)\.htm", href)
                if match:
                    next_url_num = int(match.group(1))
                    # 下一页是第2页，URL中的数字是 69
                    total_pages = next_url_num + 1

        # 生成所有分页URL
        # 第1页: https://cxcy.ysu.edu.cn/index/shou/tzgg.htm
        # 第2页: https://cxcy.ysu.edu.cn/index/shou/tzgg/69.htm
        # 第3页: https://cxcy.ysu.edu.cn/index/shou/tzgg/68.htm
        # ...
        # 第70页: https://cxcy.ysu.edu.cn/index/shou/tzgg/1.htm
        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                page_url = urljoin(base_url, "tzgg.htm")
            else:
                # 第2页对应 69, 第3页对应 68, ..., 第70页对应 1
                # URL数字 = total_pages - (page_num - 1)
                url_num = total_pages - (page_num - 1)
                page_url = urljoin(base_url, f"tzgg/{url_num}.htm")
            page_urls.append(page_url)

        return page_urls

    def run_full_crawl(self, max_pages: int = 5, max_list_pages: int = 3) -> List[Contest]:
        """执行完整爬取流程"""
        all_contests = []
        all_links = []
        visited_urls = set()

        try:
            # 1. 先爬取第一页
            print(f"开始爬取列表页: {self.LIST_URL}")
            html = self.crawler.fetch(self.LIST_URL)
            if not html:
                print("无法获取第一页")
                return []

            soup = self.crawler.parse_html(html)

            # 提取第一页的链接
            links = self._extract_contest_links(soup, self.LIST_URL)
            for link in links:
                if link["url"] not in visited_urls:
                    all_links.append(link)
                    visited_urls.add(link["url"])

            # 2. 提取分页链接并爬取
            page_urls = self._extract_pagination(soup, self.LIST_URL)
            print(f"发现 {len(page_urls)} 个分页")

            for i, page_url in enumerate(page_urls[:max_list_pages-1]):  # -1 因为第一页已爬取
                print(f"爬取分页 [{i+2}/{min(len(page_urls)+1, max_list_pages)}]: {page_url}")
                page_links = self.crawl_list_page(page_url)
                for link in page_links:
                    if link["url"] not in visited_urls:
                        all_links.append(link)
                        visited_urls.add(link["url"])
                time.sleep(1)

            print(f"总共发现 {len(all_links)} 个赛事链接")

            # 3. 爬取每个详情页
            for i, link_info in enumerate(all_links[:max_pages]):
                url = link_info["url"]
                print(f"[{i+1}/{min(len(all_links), max_pages)}] 爬取详情: {url}")

                detail = self.crawl_detail_page(url)
                if detail:
                    # 补充日期信息
                    if link_info.get("date"):
                        detail["publish_date"] = link_info["date"]

                    contest = self.save_contest(detail)
                    all_contests.append(contest)

                time.sleep(1)  # 避免请求过快

        finally:
            self.crawler.close()

        print(f"爬取完成，共处理 {len(all_contests)} 个赛事")
        return all_contests

    def close(self):
        """关闭爬虫"""
        self.crawler.close()


def get_contest_crawler(db: Session) -> YsuContestCrawler:
    """获取赛事爬虫实例"""
    return YsuContestCrawler(db)
