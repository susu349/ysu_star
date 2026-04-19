"""
验证码识别服务
"""
import io
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


class CaptchaSolver:
    """验证码识别器"""

    def __init__(self):
        self.available = HAS_PIL and HAS_TESSERACT
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """检查tesseract是否可用"""
        if not HAS_TESSERACT:
            return False
        try:
            # 尝试获取版本
            pytesseract.get_tesseract_version()
            return True
        except (pytesseract.TesseractNotFoundError, Exception):
            return False

    def solve_from_url(self, session, captcha_url: str, referer_url: str = None) -> Optional[str]:
        """从URL下载并识别验证码"""
        if not self.available or not self.tesseract_available:
            print("验证码识别不可用: 需要安装 Pillow 和 pytesseract，以及 tesseract-ocr 系统库")
            return None

        try:
            headers = {}
            if referer_url:
                headers["Referer"] = referer_url

            # 下载验证码图片
            response = session.get(captcha_url, headers=headers, timeout=30)
            response.raise_for_status()

            # 识别验证码
            return self.solve_from_bytes(response.content)

        except Exception as e:
            print(f"验证码下载/识别失败: {e}")
            return None

    def solve_from_bytes(self, image_data: bytes) -> Optional[str]:
        """从字节数据识别验证码"""
        if not self.available or not self.tesseract_available:
            return None

        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))

            # 预处理图片（提高识别率）
            image = self._preprocess_image(image)

            # 使用OCR识别
            # config: --psm 8 表示 Treat the image as a single word
            # -c tessedit_char_whitelist=... 限制字符范围
            custom_config = r'--psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = pytesseract.image_to_string(image, config=custom_config)

            # 清理结果
            text = re.sub(r'\s+', '', text)
            text = text.strip()

            if len(text) >= 4:  # 验证码通常4-6位
                return text[:6]

            return None

        except Exception as e:
            print(f"验证码识别失败: {e}")
            return None

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """预处理图片以提高识别率"""
        # 转灰度
        if image.mode != 'L':
            image = image.convert('L')

        # 二值化
        threshold = 127
        image = image.point(lambda x: 0 if x < threshold else 255, '1')

        return image


# 全局实例
_captcha_solver = None


def get_captcha_solver() -> CaptchaSolver:
    """获取验证码识别器实例"""
    global _captcha_solver
    if _captcha_solver is None:
        _captcha_solver = CaptchaSolver()
    return _captcha_solver


def setup_tesseract_instructions():
    """返回tesseract安装说明"""
    return """
验证码识别需要安装 tesseract-ocr：

Ubuntu/Debian:
    sudo apt-get install tesseract-ocr

CentOS/RHEL:
    sudo yum install tesseract

macOS:
    brew install tesseract

Windows:
    下载安装: https://github.com/UB-Mannheim/tesseract/wiki
    添加到 PATH 环境变量
"""
