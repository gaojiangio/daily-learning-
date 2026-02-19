# update.py - 自动爬取China Daily新闻并更新index.html
import requests
from bs4 import BeautifulSoup
import os

# 配置项（新手不用改）
URL = "https://global.chinadaily.com.cn/"
HTML_FILE = "index.html"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_chinadaily_news():
    """爬取China Daily首页热门新闻（标题+链接）"""
    headers = {"User-Agent": USER_AGENT}
    try:
        # 发送请求，设置超时避免卡住
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()  # 报错则触发异常
        response.encoding = "utf-8"  # 确保中文不乱码
        
        # 解析网页
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = []
        
        # 抓取首页新闻标题（适配China Daily页面结构）
        # 优先抓热门新闻区域，兼容页面结构变化
        news_elements = soup.select(".news_list li a, .top_news a, h3 a")[:10]  # 取前10条
        for elem in news_elements:
            title = elem.get_text(strip=True)
            link = elem.get("href")
            # 补全完整链接
            if link and title and len(title) > 5:  # 过滤无效内容
                if not link.startswith("http"):
                    link = f"https://global.chinadaily.com.cn{link}"
                news_list.append({"title": title, "link": link})
        
        # 保底：如果没抓到内容，用测试数据避免页面空
        if not news_list:
            news_list = [
                {"title": "Daily English: Keep learning every day", "link": "https://global.chinadaily.com.cn"},
                {"title": "Practice makes perfect", "link": "https://global.chinadaily.com.cn"}
            ]
        return news_list[:8]  # 最终取8条展示
    
    except Exception as e:
        # 任何报错都返回兜底数据，避免Action失败
        print(f"爬取新闻出错：{e}")
        return [
            {"title": "Today's English News (Backup)", "link": "https://global.chinadaily.com.cn"},
            {"title": "Learning English is fun", "link": "https://global.chinadaily.com.cn"}
        ]

def update_html(news_list):
    """更新index.html文件，替换新闻内容"""
    # 1. 读取原有HTML（如果不存在，创建基础模板）
    if not os.path.exists(HTML_FILE):
        # 生成基础HTML模板
        base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily English Learning</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; text-align: center; }
        .news-item { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .news-item a { text-decoration: none; color: #3498db; }
        .news-item a:hover { color: #2980b9; text-decoration: underline; }
        .update-time { text-align: center; color: #7f8c8d; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Daily English News (China Daily)</h1>
    <div id="news-container">
        <!-- 自动更新的新闻会在这里 -->
    </div>
    <div class="update-time" id="update-time"></div>

    <script>
        // 显示更新时间
        document.getElementById('update-time').textContent = 'Last updated: ' + new Date().toLocaleString();
    </script>
</body>
</html>
        """
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(base_html)
    
    # 2. 读取HTML并替换新闻内容
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 生成新闻HTML片段
    news_html = ""
    for idx, news in enumerate(news_list, 1):
        news_html += f"""
<div class="news-item">
    <p>{idx}. <a href="{news['link']}" target="_blank">{news['title']}</a></p>
</div>
"""
    
    # 替换占位符（如果没有占位符，直接插入到body里）
    if "<!-- 自动更新的新闻会在这里 -->" in html_content:
        updated_html = html_content.replace("<!-- 自动更新的新闻会在这里 -->", news_html)
    else:
        # 兼容自定义的index.html，在body末尾插入新闻
        updated_html = html_content.replace("</body>", f"{news_html}</body>")
    
    # 3. 保存更新后的HTML
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)
    
    print(f"成功更新{len(news_list)}条新闻到{HTML_FILE}")

if __name__ == "__main__":
    # 主流程：爬新闻 → 更新HTML
    news = get_chinadaily_news()
    update_html(news)
