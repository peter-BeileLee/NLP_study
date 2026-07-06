用 Python 手写一个**真实的微博评论情感分类器**。

我们将经历从“收集原始文本”到“数据清洗”，再到“TF-IDF 向量化”，最终“用机器学习模型完成分类预测”的全套工业级流程。

---

## 🛠️ 第一步：语料收集与定义 (Corpus & Label)

在实际工程中，语料通常是从网页爬取或数据库导出的 CSV 文件。这里我们直接在代码里模拟一个包含 **6条微博评论** 的微型 **Corpus（语料库）**。

为了好玩，我们故意在里面混入一些英文、错别字、停用词和时态变化，来模拟现实世界数据的“脏”。

```python
import pandas as pd
import numpy as np

# 1. 收集语料 (Corpus) 与 标签 (Label)
# 1 代表好评 (Positive)，0 代表差评 (Negative)
raw_data = {
    'review': [
        '这手机太赞了！真的很喜欢，the best phone ever！',
        '辣鸡服务！气死我了，以后再也不买了！',
        '虽然送货有点慢，但商品质量还可以，挺喜欢的。',
        'Bad experience! 质量太差，直接退货了。',
        '我 喜欢 这个 颜色，非常 赞！',
        '用了几天，感觉非常 bad，辣鸡。'
    ],
    'sentiment': [1, 0, 1, 0, 1, 0] # 我们的预测目标 (Label)
}

# 转化成 Pandas 的 DataFrame 格式方便切菜
df = pd.DataFrame(raw_data)
print("--- 原始采集的语料库 ---")
print(df)

```

---

## ✂️ 第二步：文本脱水与规范化 (Token & Stop Words & Lemmatization)

现在，要把这 6 条长短不一的句子切碎。因为句子中包含中英文：

1. **中文**：我们要用空格把它们分词（这里为了代码不依赖外部繁重的 `jieba` 库，我们手动处理，或者用最简单的单字/词规则）。
2. **英文**：我们把它们统一变成小写，并做一个精简版的 **Lemmatization（词形还原）**，比如把 `"cats"` 变 `"cat"`，这里我们把大写的 `"Bad"` 统一变成 `"bad"`。
3. **停用词（Stop Words）**：我们要过滤掉“了”、“的”、“太”这种高频废词。

```python
# 2. 模拟一个标准的文本清洗函数
# 定义我们想扔掉的停用词
STOP_WORDS = {'了', '的', '太', '我', '在', '以', '后', '个', 'the', 'ever'}

def clean_text(text):
    # a. 统一转成小写（英文规范化）
    text = text.lower()
    
    # b. 粗暴分词 (Tokenization) 
    # 实际工业界中文用 jieba 分词，英文按空格。这里我们用空格和符号做个简单切分
    for punc in ['！', '，', '。', '.', '!']:
        text = text.replace(punc, ' ')
    tokens = text.split()
    
    # c. 过滤停用词 (Stop Words Filtering)
    cleaned_tokens = [t for t in tokens if t not in STOP_WORDS]
    
    # 将洗干净的积木重新用空格拼回成一句话，方便后面算 TF-IDF
    return " ".join(cleaned_tokens)

# 执行清洗
df['cleaned_review'] = df['review'].apply(clean_text)
print("\n--- 清洗脱水后的语料 ---")
print(df[['cleaned_review', 'sentiment']])

```

---

## 📐 第三步：符号变矩阵 (Vocabulary & TF-IDF 结合)

现在我们要祭出我们的映射盒子 **$\Phi$**。我们不使用简单的 `Bag of Words`，而是使用 **`TF-IDF`** 算法，把清洗后的句子翻译成固定长度的数学向量。

为了让你看清底层的数学黑盒，我们直接调用 `sklearn` 库中的 `TfidfVectorizer`。

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# 3. 构建 TF-IDF 转换器
# binarize/norm 会自动处理固定长度。这里它会自动扫描所有文本，生成专属词表 (Vocabulary)
tfidf_wizard = TfidfVectorizer()

# 让转换器去学习我们的词表，并把文本转化为数字特征矩阵 (Feature Matrix X)
X_tfidf = tfidf_wizard.fit_transform(df['cleaned_review']).toarray()

# 顺便看一眼它偷偷生成的词表字典 (Vocabulary) 长的啥样
print("\n--- 智能转换器自动生成的词表 (Vocabulary) ---")
print(tfidf_wizard.get_feature_names_out())
print(f"词表大小 (也就是固定长度 d) = {len(tfidf_wizard.get_feature_names_out())}")

print("\n--- 最终生成的固定长度数字矩阵 (X) ---")
print(X_tfidf)

```

> **💡 此时的数字代表什么？**
> 你会看到一个 6 行 $\times$ 14 列 的二维数字矩阵。
> * **6 行**：代表我们的 6 条评论（样本）。
> * **14 列**：因为全语料去重洗净后只有 14 个核心词。
> * **里面的每一个小数**：就是该词在这一句里的 **TF-IDF 得分**。如果某个词在全剧组都高频出现，它的得分就会被压低；如果是特征词（如“辣鸡”），得分就会很高。
> 
> 

---

## 🤖 第四步：喂给模型，训练与理解 (Supervised Learning)

数字矩阵有了（**Feature $X$**），标准答案也有了（**Label $y$**）。现在我们挑选一个经典的机器学习二分类模型：**朴素贝叶斯分类器（Naive Bayes）** 或 **逻辑回归（Logistic Regression）** 来进行监督学习。

模型会在底层疯狂做矩阵乘法，调整自己的参数 $W$，去寻找数字特征和 0/1 标签之间的数学规律。

```python
from sklearn.linear_model import LogisticRegression

# 4. 初始化一个逻辑回归模型
model = LogisticRegression()

# 准备好 Feature (X) 和 Label (y)
X = X_tfidf
y = df['sentiment'].to_numpy()

# 开启监督学习：让模型在数据里“悟”出规律 (训练 Fit)
model.fit(X, y)

print("\n[INFO] 模型训练完成！它已经学会了如何根据 TF-IDF 的数字大小来判断情绪。")

```

---

## 🔮 第五步：线上实战预测 (Test Set & Evaluation)

模型到底学得怎么样？我们写一句**全新的、模型从来没见过的**微博评论，丢给它试试！

```python
# 5. 模拟一条全然陌生的测试评论 (Test Instance)
new_review = "服务挺好，非常赞，我很喜欢！"

# 第一步：必须用一模一样的流水线对它进行清洗
cleaned_new = clean_text(new_review)

# 第二步：必须用一模一样的转换器，把它变成固定长度（14维）的数字向量
# 注意：这里只用 transform，绝对不能用 fit_transform，否则维度就乱了
new_X = tfidf_wizard.transform([cleaned_new]).toarray()

# 第三步：让模型闭卷考试，输出预测结果
prediction = model.predict(new_X)
probability = model.predict_proba(new_X) # 顺便看看概率

print("\n--- 陌生新样本预测测试 ---")
print(f"原始测试文本：{new_review}")
print(f"转化后的14维数字向量：\n{new_X}")
print(f"预测结果：{'👍 正面好评' if prediction[0] == 1 else '👎 负面差评'}")
print(f"模型预测它是好评的置信概率：{probability[0][1] * 100:.2f}%")

```

---

## 🗺️ 最后的硬核复盘：整个流程你是如何实现理解的？

通过上面的实例，你已经亲手实现了一个最经典的 NLP 闭环。我们用前面学到的所有概念来复盘它是怎么成功的：

1. **为什么模型能猜对新句子？**
因为新句子里的“赞”和“喜欢”经过 **TF-IDF** 计算后，在第 7 列和第 11 列（假设）上产生了很高的数值。
2. **过拟合与欠拟合的体现**：
如果我们的语料库只有这 6 条（数据量太小），模型可能会产生**过拟合（Overfitting）**。它会死记硬背地认为：“只要出现‘颜色’两个字，就一定是好评”。一旦以后有人骂“这个颜色丑死了”，模型因为死记硬背，依然会错误地输出“好评”。
3. **如何评估这个模型？**
在真实工业界，我们会把 10 万条数据拆分成 **Training Set（训练集）** 和 **Test Set（测试集）**。然后画出 **Confusion Matrix（混淆矩阵）**，计算出 **Precision（精确率，别冤枉好评论）** 和 **Recall（召回率，别漏掉差评）**，最后盯死 **F1 Score** 来决定这个模型能不能上线。

---

## 🎯 接下来，你应该如何进行后续的学习？

既然你已经把最底层的“数据分析”与“NLP古典特征提取”打通了，建议你按照以下三步继续通关：

* **第一阶段：玩转古典机器学习（熟练使用 Scikit-Learn）**
* **怎么做**：多找几个不同的数据集（比如预测泰坦尼克号生存率、鸢尾花分类）。
* **核心攻克**：学会如何做真正的 **Training/Test Set 划分**（使用 `train_test_split`），并用代码把 **Confusion Matrix**、**Classification Report**（打印 Precision, Recall, F1）真正跑出来。


* **第二阶段：跨越到现代 NLP（理解词向量 Word Embedding）**
* **怎么做**：去学习 `Word2Vec` 或 `FastText` 算法。
* **核心攻克**：你会理解为什么现代 AI 不需要用 TF-IDF 这种干巴巴数次数的方法，而是给每个词赋予一个 300 维的“空间几何坐标”，让“猫”和“狗”自动在数学空间里聚在一起。


* **第三阶段：拥抱大模型与深度学习（深度特征提取）**
* **怎么做**：尝试了解神经网络是如何通过自动提取 **Feature（特征）**，免去了我们手动清洗停用词、手动还原词形的痛苦。这也是 BERT、GPT 等大模型的底层底座。