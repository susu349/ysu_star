"""测试验证码下载"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.services.contest.captcha_downloader import get_captcha_downloader
from campus_ai.core.utils.captcha_solver import setup_tesseract_instructions


def test_captcha():
    """测试验证码下载"""
    print("=" * 80)
    print("测试验证码下载")
    print("=" * 80)

    # 测试URL
    test_url = "https://cxcy.ysu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2020326649&wbfileid=16588093"

    print(f"\n测试URL: {test_url}")

    # 检查OCR可用性
    downloader = get_captcha_downloader()

    if not downloader.solver.available:
        print("\n⚠️  OCR库未安装 (Pillow 或 pytesseract)")
        print("请运行: uv add Pillow pytesseract")
        return

    if not downloader.solver.tesseract_available:
        print("\n⚠️  tesseract-ocr 未安装")
        print(setup_tesseract_instructions())
        print("\n提示: 即使没有OCR，你也可以手动下载附件，网页内容已足够AI提取信息")
        return

    print("\n✅ OCR可用，尝试下载...")

    # 尝试下载
    content = downloader.download_with_captcha(test_url, max_attempts=2)

    if content:
        print(f"\n✅ 下载成功！大小: {len(content)} 字节")

        # 保存测试
        test_file = "/tmp/test_download.pdf"
        with open(test_file, "wb") as f:
            f.write(content)
        print(f"已保存到: {test_file}")

        # 检查是否是有效的PDF
        if content[:4] == b"%PDF":
            print("✅ 是有效的PDF文件")
        else:
            print(f"⚠️  文件头: {content[:20]}")
    else:
        print("\n❌ 下载失败")
        print("\n提示:")
        print("1. 验证码识别率可能不高，可以多试几次")
        print("2. 网页内容已足够AI提取信息，附件不是必需的")


if __name__ == "__main__":
    test_captcha()
