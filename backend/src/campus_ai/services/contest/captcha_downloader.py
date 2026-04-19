"""
燕山大学网站验证码下载器
"""
import re
import time
import random
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import httpx
from bs4 import BeautifulSoup

from ...core.utils.captcha_solver import get_captcha_solver, setup_tesseract_instructions


class YsuCaptchaDownloader:
    """燕山大学验证码下载器"""

    def __init__(self):
        self.solver = get_captcha_solver()
        self.base_url = "https://cxcy.ysu.edu.cn"

    def download_with_captcha(self, url: str, max_attempts: int = 3) -> Optional[bytes]:
        """
        带验证码识别的下载

        Args:
            url: 附件下载URL
            max_attempts: 最大尝试次数

        Returns:
            下载的文件内容(bytes)，失败返回None
        """
        session = httpx.Client(
            timeout=60,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        try:
            for attempt in range(max_attempts):
                print(f"验证码下载尝试 {attempt + 1}/{max_attempts}")

                # Step 1: 先访问下载页面，获取验证码页面
                html = self._get_captcha_page(session, url)
                if not html:
                    print("无法获取验证码页面")
                    continue

                # Step 2: 检查是不是直接就是文件（不需要验证码）
                if self._is_file_content(html):
                    print("直接获取到文件，无需验证码")
                    return html.encode("latin-1")  # 假设是二进制

                # Step 3: 需要验证码，检查OCR是否可用
                if not self.solver.available or not self.solver.tesseract_available:
                    print("OCR不可用，无法识别验证码")
                    print(setup_tesseract_instructions())
                    return None

                # Step 4: 解析验证码页面，获取验证码图片URL
                captcha_img_url = self._extract_captcha_image_url(html)
                if not captcha_img_url:
                    print("无法找到验证码图片")
                    continue

                # Step 5: 获取验证码图片并识别
                captcha_code = self._get_and_solve_captcha(session, captcha_img_url, url)
                if not captcha_code:
                    print(f"验证码识别失败 (尝试 {attempt + 1}/{max_attempts})")
                    time.sleep(1)
                    continue

                print(f"识别到验证码: {captcha_code}")

                # Step 6: 提交验证码下载文件
                file_content = self._submit_captcha_and_download(session, url, captcha_code)
                if file_content:
                    print("验证码通过，下载成功！")
                    return file_content

                print(f"验证码可能错误，重试... (尝试 {attempt + 1}/{max_attempts})")
                time.sleep(1)

            print(f"验证码下载失败，已尝试 {max_attempts} 次")
            return None

        finally:
            session.close()

    def _get_captcha_page(self, session, url: str) -> Optional[str]:
        """获取验证码页面"""
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取验证码页面失败: {e}")
            return None

    def _is_file_content(self, content: str) -> bool:
        """判断是不是文件内容（而不是HTML验证码页面）"""
        # 如果不是以HTML开头，可能是文件
        if not content.strip().startswith("<!DOCTYPE") and not content.strip().startswith("<html"):
            return True

        # 检查是否有验证码页面的特征
        if "请输入验证码下载附件" in content or "codeValue" in content:
            return False

        return True

    def _extract_captcha_image_url(self, html: str) -> Optional[str]:
        """从HTML中提取验证码图片URL"""
        try:
            soup = BeautifulSoup(html, "lxml")

            # 查找验证码图片
            # 方式1: 找 id="codeimg"
            img = soup.find("img", id="codeimg")
            if img and img.get("src"):
                return urljoin(self.base_url, img["src"])

            # 方式2: 从脚本中解析
            # document.write('<img src="/system/resource/js/filedownload/createimage.jsp?randnum=...">')
            script_pattern = r'src=["\']([^"\']*createimage\.jsp[^"\']*)["\']'
            match = re.search(script_pattern, html)
            if match:
                return urljoin(self.base_url, match.group(1))

            return None

        except Exception as e:
            print(f"提取验证码图片URL失败: {e}")
            return None

    def _get_and_solve_captcha(self, session, img_url: str, referer_url: str) -> Optional[str]:
        """获取验证码图片并识别"""
        try:
            # 添加随机数参数
            if "?" in img_url:
                img_url = f"{img_url}&randnum={random.randint(100000, 999999)}"
            else:
                img_url = f"{img_url}?randnum={random.randint(100000, 999999)}"

            # 下载图片
            headers = {"Referer": referer_url}
            response = session.get(img_url, headers=headers)
            response.raise_for_status()

            # 识别验证码
            code = self.solver.solve_from_bytes(response.content)
            return code

        except Exception as e:
            print(f"获取/识别验证码失败: {e}")
            return None

    def _submit_captcha_and_download(self, session, original_url: str, captcha_code: str) -> Optional[bytes]:
        """提交验证码并下载文件"""
        try:
            # 构建带验证码的URL
            if "?" in original_url:
                download_url = f"{original_url}&codeValue={captcha_code}"
            else:
                download_url = f"{original_url}?codeValue={captcha_code}"

            # 下载文件
            headers = {"Referer": original_url}
            response = session.get(download_url, headers=headers)
            response.raise_for_status()

            # 检查是不是又回到了验证码页面
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                html = response.text
                if "请输入验证码下载附件" in html or "codeValue" in html:
                    print("返回了验证码页面，验证码可能错误")
                    return None

            # 返回二进制内容
            return response.content

        except Exception as e:
            print(f"提交验证码/下载失败: {e}")
            return None


# 全局实例
_downloader = None


def get_captcha_downloader() -> YsuCaptchaDownloader:
    """获取验证码下载器实例"""
    global _downloader
    if _downloader is None:
        _downloader = YsuCaptchaDownloader()
    return _downloader
