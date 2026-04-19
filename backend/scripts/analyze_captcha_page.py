"""分析验证码下载页面"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campus_ai.core.utils.crawler_base import BaseCrawler


def analyze_captcha_page():
    """分析验证码页面"""
    print("=" * 80)
    print("分析验证码下载页面")
    print("=" * 80)

    # 先用之前下载的PDF链接测试
    test_url = "https://cxcy.ysu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2020326649&wbfileid=16588093"

    crawler = BaseCrawler("https://cxcy.ysu.edu.cn")

    try:
        print(f"\n尝试下载: {test_url}")
        html = crawler.fetch(test_url)

        if html:
            print(f"\n返回内容长度: {len(html)}")
            print(f"\n内容前1000字符:")
            print("-" * 80)
            print(html[:1000])
            print("-" * 80)

            # 保存到文件方便分析
            with open("/tmp/captcha_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n完整内容已保存到: /tmp/captcha_page.html")

            # 用BeautifulSoup分析
            soup = crawler.parse_html(html)

            print(f"\n找验证码图片:")
            imgs = soup.find_all("img")
            print(f"找到 {len(imgs)} 个图片:")
            for i, img in enumerate(imgs):
                src = img.get("src", "")
                print(f"  {i+1}. {src}")

            print(f"\n找表单:")
            forms = soup.find_all("form")
            print(f"找到 {len(forms)} 个表单:")
            for i, form in enumerate(forms):
                action = form.get("action", "")
                method = form.get("method", "GET")
                print(f"  {i+1}. action={action}, method={method}")
                inputs = form.find_all("input")
                for inp in inputs:
                    inp_name = inp.get("name", "")
                    inp_type = inp.get("type", "")
                    inp_value = inp.get("value", "")
                    print(f"      <input name={inp_name} type={inp_type} value={inp_value[:50]}>")

    finally:
        crawler.close()


if __name__ == "__main__":
    analyze_captcha_page()
