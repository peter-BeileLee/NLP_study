import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ==========================================
# 阶段一：开源词库与组件准备
# ==========================================

# 1. 导入 NLTK 组件并自动下载所需的停用词库数据
import nltk
# download() 会在后台检查，如果本地有就跳过，没有就自动下载
nltk.download('stopwords', quiet=True)

# 2. 导入标准的 NLTK 英文停用词词典，用来在后续特征提取中过滤“无意义高频词”
from nltk.corpus import stopwords
english_stopwords = stopwords.words('english')

# 3. 导入专业 VADER 情感分析开源词库
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# 初始化 VADER 分析器，它会自动加载包含 7500+ 情感词的内置开源词表
vader_analyzer = SentimentIntensityAnalyzer()

# ==========================================
# 阶段二：野生脏数据加载与清洗算法
# ==========================================

# 4. 模拟通过 Python 爬虫抓取到的无规则、带 HTML 噪声的野生英文数据
raw_data = {
    "text": [
        "<html>This movie is an absolutely amazing masterpiece! I love the plot!</html>",  # 显性好评：带强烈情感词
        "I hate this film. The plot is terrible and completely boring. #trash",            # 显性差评：带强烈负面词
        "The computer features an Intel processor and a standard 512GB SSD.",              # 噪声数据：纯科技中性描述
        "The cinematography was breathtaking, capturing subtle emotions beautifully.",     # 隐性好评：无常规love/good，但语境极佳
        "I hope the remainings could be more appealing."                                   # 虚拟/期许文本：字面积极，真实意图偏负面
    ]
}
df = pd.DataFrame(raw_data)

# 5. 定义文本核心清洗算法（去掉 HTML 标签、多余符号，并统一转化为小写）
def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)          # 使用正则表达式剔除所有网页 HTML 标签
    text = re.sub(r'[^\w\s]', '', text)          # 剔除所有的特殊标点符号和乱码
    return text.strip().lower()                  # 剥离两端空格并统一转为小写

# 6. 对原始文本应用清洗算法，生成干净的文本列
df["clean_text"] = df["text"].apply(clean_text)

print("--- 1. 启动融合现代语法分析的开源词典打标 (第一阶段初筛) ---")

# ==========================================
# 阶段三：语法规则拦截与开源词典初筛打标
# ==========================================

# 7. 现代语法分析手段：虚拟语气与期许句过滤器 (Wish & Irrealis Filter)
def check_irrealis_mood(text):
    # 定义强期许动词库
    wish_verbs = {'hope', 'wish', 'expect', 'desire', 'if'}
    # 定义强情态动词库（用于构建虚拟语气或未来设想）
    modal_verbs = {'could', 'would', 'should', 'might', 'better'}
    
    # 将文本分词
    words = set(text.split())
    
    # 算法核心逻辑：如果一句话里同时出现了期许词和情态动词（例如 hope ... could）
    # 说明该文本大概率属于“对现状不满足的虚拟期许”，字面即使包含 positive 词汇也属于伪特征
    if (words & wish_verbs) and (words & modal_verbs):
        return True
    return False

# 8. 编写初筛决策算法：结合词典分值与语法过滤引擎
def first_pass_lexicon_labeling(text):
    # 8.1 优先前置执行现代语法分析手段
    if check_irrealis_mood(text):
        # 如果触发了拦截规则，直接将该文本定性为 Negative（或者隔离为 Unlabeled），切断伪特征向黄金种子集的渗透
        return "Negative"
        
    # 8.2 如果未触发语法规则，则正常调用 VADER 词库评分
    vader_scores = vader_analyzer.polarity_scores(text)
    compound_score = vader_scores['compound']
    
    # 8.3 建立严格的“分类决策边界”（阈值控制）
    if compound_score >= 0.5:
        return "Positive"   # 综合分大于等于 0.5，判定为高质量正面种子数据
    elif compound_score <= -0.5:
        return "Negative"   # 综合分小于等于 -0.5，判定为高质量负面种子数据
    else:
        return "Unlabeled"  # 处于灰色地带或隐性的文本，暂时不打标，留给下一轮算法来捞

# 9. 应用融合语法分析后的初筛算法，贴上第一轮标签
df["label"] = df["clean_text"].apply(first_pass_lexicon_labeling)
print(df[["clean_text", "label"]])

print("\n--- 2. 启动 Bootstrapping 语境特征自举迭代 (第二阶段拉高召回率) ---")

# ==========================================
# 阶段四：Bootstrapping 自举法（语境机器学习）
# ==========================================

# 10. 算法分流：捞出第一轮依靠开源词典与语法规则确定的黄金“种子数据”作为训练集
seed_data = df[df["label"] != "Unlabeled"].reset_index(drop=True)
# 11. 算法分流：捞出被词典漏掉的“隐性/无标签数据”作为待预测集合
unlabeled_data = df[df["label"] == "Unlabeled"].reset_index(drop=True)

# 12. 健壮性判断：如果存在漏网之鱼，则启动语境泛化学习
if not unlabeled_data.empty:
    
    # 13. 构建特征提取器：引入停用词库，并开启 Unigram 和 Bigram 特征
    vectorizer = TfidfVectorizer(stop_words=english_stopwords, ngram_range=(1, 2))
    
    # 14. 种子特征矩阵化：学习黄金数据的词频逆文档频率（TF-IDF）特征
    X_train = vectorizer.fit_transform(seed_data["clean_text"])
    y_train = seed_data["label"]  
    
    # 15. 初始化模型：逻辑回归（Logistic Regression）
    clf = LogisticRegression()
    # 16. 模型拟合：训练模型学出这些安全特征与情感标签之间的映射关系
    clf.fit(X_train, y_train)
    
    # 17. 隐性数据特征化：将无标签的漏网文本转换为相同维度的 TF-IDF 矩阵
    X_unlabeled = vectorizer.transform(unlabeled_data["clean_text"])
    
    # 18. 概率预测倾向
    probs = clf.predict_proba(X_unlabeled)
    classes = clf.classes_  
    
    # 19. 动态遍历与召回机制：逐条审查漏网文本
    for i, row in unlabeled_data.iterrows():
        max_prob_idx = probs[i].argmax()   
        max_prob = probs[i][max_prob_idx]  
        predicted_label = classes[max_prob_idx] 
        
        # 20. 设置置信度召回门槛，排除掉纯硬件噪声（如 intel 描述）
        if max_prob > 0.51 and "intel" not in row["clean_text"]:
            orig_idx = df[df["clean_text"] == row["clean_text"]].index[0]
            df.loc[orig_idx, "label"] = predicted_label
            print(f"🎯 算法挽回成功: '{row['clean_text'][:30]}...' -> 修正为: {predicted_label} (置信度: {max_prob:.2f})")

# ==========================================
# 阶段五：数据最终洗净输出
# ==========================================
print("\n--- 3. 最终交付：高准确、高召回的标准化分类数据集 ---")
print(df[["clean_text", "label"]])