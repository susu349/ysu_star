"""
爬虫基础模块 - 用于从官网获取数据
"""
import time
import hashlib
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from ..config import get_settings

settings = get_settings()


class BaseCrawler:
    """基础爬虫类"""

    def __init__(self, base_url: str, delay: int = None):
        self.base_url = base_url
        self.delay = delay or settings.CRAWLER_DELAY
        self.timeout = settings.CRAWLER_TIMEOUT
        self.session = httpx.Client(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.visited_urls: set = set()

    def _wait(self):
        """请求延迟，避免被封"""
        if self.delay > 0:
            time.sleep(self.delay)

    def fetch(self, url: str) -> Optional[str]:
        """获取页面内容"""
        if url in self.visited_urls:
            return None

        try:
            self._wait()
            response = self.session.get(url)
            response.raise_for_status()
            self.visited_urls.add(url)
            return response.text
        except Exception as e:
            print(f"抓取失败 {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, "lxml")

    def extract_links(self, soup: BeautifulSoup, base_url: str = None) -> List[str]:
        """提取页面中的所有链接"""
        base_url = base_url or self.base_url
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(base_url, href)
            # 只保留同域名链接
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
        return list(set(links))

    def extract_text(self, soup: BeautifulSoup) -> str:
        """提取纯文本内容"""
        # 移除script和style标签
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # 清理多余空行
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""

    def close(self):
        """关闭会话"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def content_hash(content: str) -> str:
    """计算内容哈希，用于去重"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def normalize_url(url: str) -> str:
    """标准化URL"""
    parsed = urlparse(url)
    # 移除末尾斜杠
    path = parsed.path.rstrip("/")
    return parsed._replace(path=path).geturl()
