import os
import re
import json
import xml.etree.ElementTree as ET
import requests

# ==========================================
# 1. 配置爬取源：使用标准新闻聚合源 (RSS Feeds)
# ==========================================
# 我们选取了科技、体育、商业三个经典分类的真实野生数据源
rss_sources = {
    "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "Sports": "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
    "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"
}

# 设置请求头（User-Agent），模拟浏览器访问，防止被反爬虫机制拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# 2. 自动化文件工程：创建分类存储目录
# ==========================================
BASE_DIR = "./raw_news_dataset"
os.makedirs(BASE_DIR, exist_ok=True) # 创建主数据集总文件夹

print("--- 正在初始化本地文件目录 ---")
for category in rss_sources.keys():
    # 根据类别名字，自动创建子文件夹（例如 ./raw_news_dataset/Technology）
    category_path = os.path.join(BASE_DIR, category)
    os.makedirs(category_path, exist_ok=True)
    print(f"目录已就绪: {category_path}")

print("\n--- 开始执行网络数据爬取流水线 ---")

# ==========================================
# 3. 网络爬取与解析核心算法
# ==========================================
for category, url in rss_sources.items():
    print(f"\n正在爬取 [{category}] 类别的数据中...")
    
    try:
        # 发送网络请求获取 XML 数据
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            # RSS 返回的是 XML 格式，我们使用 ElementTree 算法进行结构化解析
            root = ET.fromstring(response.content)
            
            # 在 XML 中定位所有的文章节点（item）
            articles = root.findall('.//item')
            print(f"成功抓取到 {len(articles)} 条原始新闻数据。")
            
            saved_count = 0
            for idx, article in enumerate(articles):
                # 提取新闻的标题和摘要描述
                title = article.find('title').text if article.find('title') is not None else ""
                description = article.find('description').text if article.find('description') is not None else ""
                
                # 如果没有核心内容，跳过当前条目
                if not title and not description:
                    continue
                
                # 组合成完整的野生 Raw Data 文本
                raw_text = f"Title: {title}\nDescription: {description}"
                
                # ==========================================
                # 4. 自动化持久化储存
                # ==========================================
                # 清洗标题，移除不能做文件名的特殊字符（如 \ / : * ? " < > |）
                safe_title = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', title)[:30] # 截取前30个字防止文件名超长
                file_name = f"{idx:03d}_{safe_title}.txt"
                
                # 构建最终的存储路径
                file_path = os.path.join(BASE_DIR, category, file_name)
                
                # 将爬取到的野生文本写入对应的分类文件夹中
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(raw_text)
                
                saved_count += 1
                # 为了防止控制台刷屏，这里只展示前 3 条的储存动态
                if saved_count <= 3:
                    print(f"  [保存成功] -> {file_path}")
            
            print(f"==> [{category}] 类别处理完毕，共成功储存 {saved_count} 个原始文本文件。")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ 爬取过程中发生异常: {e}")

print("\n--- 所有 Raw Data 爬取并分类储存完毕！ ---")
print(f"请检查当前目录下的 {BASE_DIR} 文件夹。")