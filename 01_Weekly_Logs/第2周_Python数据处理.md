## 1. 什么是数据分析与预处理？（What & Why）

### 通俗易懂的解释

如果说机器学习模型（比如神经网络、逻辑回归）是一个“高端破壁机”**，那原始数据（CSV、JSON 文件）就是刚从地里拔出来的、带着泥土的**“生冷果蔬”。
你不能把带泥的土豆直接扔进破壁机，否则机器会坏掉（报错），或者做出的果汁很难喝（模型准确率极低）。

**Python 数据分析**就是做菜前的“洗菜、切菜、挑拣”过程。我们需要把杂乱的文件读进 Python，把里面的坏果子（脏数据、缺失值）扔掉，按照规则切块（筛选、分组），最后才能喂给模型。

### 数学与底层化解释

在计算机底层，任何机器学习算法的本质都是**矩阵运算**。
假设你的模型是一组矩阵乘法： $\mathbf{Y} = \mathbf{W}\mathbf{X} + \mathbf{b}$。
原始的 CSV 或 JSON 文本文件无法直接参与这样的数学运算。数据预处理的底层逻辑，就是利用 **NumPy** 和 **Pandas** 将磁盘上的异构文件（Heterogeneous Files）加载到内存中，并将其转化为规整的、连续存储的**高维张量（Tensor/Array）** $\mathbf{X}$。

---

## 2. 三大神器（NumPy, Pandas, Matplotlib）的底层定位

在写代码之前，我们要先搞清楚这三个库在计算机底层分别扮演什么角色：

* **NumPy（底层数值加速器）**：
* **核心语法结构**：`ndarray`（多维数组）。
* **底层原理**：Python 原生的列表（List）在内存里是分散存储的，且带有大量的类型检查，计算极慢。NumPy 是用 **C 语言**写的，它在内存中开辟一块**连续的空间**来存放同类型的数据。它可以实现 **SIMD（单指令多数据流）** 硬件加速，让几十万行数据的矩阵乘加在一瞬间完成。


* **Pandas（结构化数据魔术师）**：
* **核心语法结构**：`DataFrame`（二维表格，由行索引和列名组成）。
* **底层原理**：基于 NumPy 构建。NumPy 只能存纯数字，而 Pandas 允许每一列有不同的类型（如第一列是姓名文本，第二列是年龄数字）。它就像是一个内存中的“超级智能 Excel”。


* **Matplotlib（数据画笔）**：
* **底层原理**：负责把数字映射成屏幕上的像素点。它将复杂的矩阵数据转化为直观的几何图形（线、柱、点），供工程师洞察数据的分布规律。



---

## 3. 常用语法与算法：全流程通俗实操

我们直接通过一条标准的工业级数据清洗流水线，来讲解最常用的核心语法。

### ① 数据入口：文件读取（CSV & JSON）

我们首先需要把硬盘里的文件拉到内存里变成 `DataFrame`。

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 读取 CSV 文件（逗号分隔的纯文本表格）
# 底层算法：Pandas 会扫描文件，按逗号切分每一行，并自动推断每一列的数据类型
df_csv = pd.read_csv('user_data.csv')

# 2. 读取 JSON 文件（键值对/嵌套结构）
# 底层算法：将 JSON 字符串解析为 Python 字典树，再展平（Flatten）为二维表格
df_json = pd.read_json('user_logs.json')

```

---

### ② 核心手术刀：DataFrame 筛选

拿到了大表（假设变量名叫 `df`），我们通常只需要特定的一部分数据。

* **底层算法（布尔掩码 Boolean Masking）**：
当你输入 `df['age'] > 18` 时，Pandas 并不会立刻去删数据，而是在底层通过 NumPy 快速生成一个由 `True` 和 `False` 组成的、长度相等的**布尔数组**。当你把这个数组传回 `df[...]` 时，底层只会拷贝内存中对应位置为 `True` 的那几行。

```python
# 常用语法 1：单条件筛选（找出所有成年用户）
adult_users = df[df['age'] > 18]

# 常用语法 2：多条件筛选（注意：条件之间用 & (且)、| (或) 连接，且每个条件必须加括号）
# 找出年龄大于 18 岁且消费金额（spend）大于 500 的 VIP 用户
vip_heavy_users = df[(df['age'] > 18) & (df['spend'] > 500)]

```

---

### ③ 分组统计（Group By）

你想知道不同性别的用户，平均消费了多少钱？

* **底层算法（Split-Apply-Combine 拆分-应用-合并）**：
1. **Split（拆分）**：扫描指定的列（如性别），在内存中建立一个哈希表（Hash Table），把相同性别行的内存地址归到一组。
2. **Apply（应用）**：对每个独立的组，调用底层的 NumPy 聚合函数（如 `mean()`、`sum()`）计算结果。
3. **Combine（合并）**：将各个小组的计算结果粘合在一起，吐出一张全新的、以分组字段为索引的紧凑表。



```python
# 常用语法：按照 'gender' 分组，计算 'spend' 列的平均值
gender_spend = df.groupby('gender')['spend'].mean()

# 高级玩法：一次性计算平均值（mean）和总和（sum）
gender_stats = df.groupby('gender')['spend'].agg(['mean', 'sum'])

```

---

### ④ 文本长度统计（NLP 任务前哨）

如果某一列是文本数据（比如用户评论 `comment`），我们需要统计每个句子的字数。

```python
# 常用语法：利用 .str 矢量化字符串操作
# 底层算法：底层在 C 语言层面运行循环，调用 len() 函数，避免了笨重的 Python 显式 for 循环
df['text_len'] = df['comment'].str.len()

# 结合筛选：过滤掉小于 3 个字的垃圾短评
df_filtered = df[df['text_len'] >= 3]

```

---

### ⑤ 类别分布统计（Value Counts）

在做机器学习分类前，**必须**看一眼各类别的占比情况，防止出现“严重的样本不平衡”。

```python
# 常用语法：统计 'label' 这一列中，每个类别分别出现了多少次
class_distribution = df['label'].value_counts()

# 如果想直接看百分比占比，加入 normalize=True参数
class_percentage = df['label'].value_counts(normalize=True)

```

> **大白话**：它会告诉你，“正常用户”占了 95%，“作弊用户”占了 5%。如果比例太悬殊，后续千万不能盲目相信 Accuracy（准确率）！

---

### ⑥ 数据可视化：Matplotlib 作图

用前述统计好的数据，一键给模型画图。

```python
# 1. 柱状图 (Bar Chart) —— 完美展示类别分布统计
# 拿到数据
counts = df['label'].value_counts()
# 语法：传入 X 轴的标签（类别名）和 Y 轴的数值（频数）
plt.bar(counts.index, counts.values, color='orange')
plt.title('Label Distribution') # 标题
plt.xlabel('Class')             # X轴名字
plt.ylabel('Count')             # Y轴名字
plt.show()                      # 将图表渲染到屏幕上

# 2. 直方图 (Histogram) —— 完美展示文本长度分布
# 底层算法：自动将连续的长度范围（如0-100字）切分成 N 个均匀的“水桶(bins)”，并数出落入每个水桶的样本数
plt.hist(df['text_len'], bins=30, edgecolor='black')
plt.title('Text Length Analysis')
plt.xlabel('Length')
plt.ylabel('Frequency')
plt.show()

```

---

## 🗺️ 终极代码串联（可直接运行的工业标准模板）

我们把上述零散的语法组合成一段完整的闭环脚本：

```python
import pandas as pd
import matplotlib.pyplot as plt

# 步骤 1：读取大盘数据
df = pd.read_csv('mall_customers.csv')

# 步骤 2：数据清洗与特征构造（文本长度统计）
# 假设 'feedback' 列是客户填写的反馈文本
df['feedback_len'] = df['feedback'].str.len()

# 步骤 3：DataFrame 筛选（只保留留下了有效反馈，且消费评分大于 50 的高质量客户）
clean_df = df[(df['feedback_len'] > 5) & (df['spending_score'] > 50)]

# 步骤 4：分组统计（看看不同 VIP 等级客户的平均反馈长度）
print("--- 各等级VIP平均反馈字数 ---")
print(clean_df.groupby('vip_level')['feedback_len'].mean())

# 步骤 5：类别分布统计并画图
vip_counts = clean_df['vip_level'].value_counts()
plt.bar(vip_counts.index, vip_counts.values)
plt.title('VIP Level Distribution of Active Users')
plt.show()

```
## 实例实战
### 🏢 案例一：房价数据分析（NumPy + Pandas 联动）
> 场景： 拿到了一个房地产的原始表格，我们需要清洗数据、提取特征，并将其转化为机器学习算法直接可用的 NumPy 矩阵。

```Python
import pandas as pd
import numpy as np

# 1. 模拟创建原始的房地产 DataFrame 数据（模拟从 CSV 读入）
raw_data = {
    'neighborhood': ['Chaoyang', 'Haidian', 'Chaoyang', 'Xicheng', 'Haidian'],
    'rooms': [3, 2, np.nan, 4, 3], # 包含一个缺失值 NaN
    'area_sqm': [120, 85, 90, 150, 110],
    'price_myr': [8.5, 7.2, 5.8, 12.0, 9.1]
}
df = pd.DataFrame(raw_data)
print("--- 原始数据 ---")
print(df)

# 2. 用 Pandas 清洗数据：用房间数的“中位数”填充缺失值
room_median = df['rooms'].median()
df['rooms'] = df['rooms'].fillna(room_median)

# 3. 特征工程：用 Pandas 计算一个新特征“每平米单价”
df['price_per_sqm'] = df['price_myr'] / df['area_sqm']

print("\n--- 清洗与特征工程后的数据 ---")
print(df)

# 4. 底层转换：将 Pandas 的数值列彻底转换为 NumPy 矩阵，准备喂给机器学习模型
# 我们只提取 rooms, area_sqm, price_per_sqm 作为特征矩阵 X
X = df[['rooms', 'area_sqm', 'price_per_sqm']].to_numpy()

print("\n--- 最终喂给模型的 NumPy 矩阵 (X) ---")
print(X)
print(f"矩阵形状 (Shape): {X.shape}") # 输出 (5, 3)，代表 5 个样本，每个样本 3 个特征

```
### 📈 案例二：股票/销售趋势分析与预测线展示（Matplotlib + NumPy）
> 场景： 我们有一组连续的销售数据，我们想用 NumPy 拟合出一条趋势线（基础回归），并用 Matplotlib 把它清晰地画出来。

```Python
import numpy as np
import matplotlib.pyplot as plt

# 1. 用 NumPy 生成模拟的销售时间数据（第 1 天到第 10 天）
days = np.arange(1, 11)

# 2. 模拟实际销售额（带有一些随机波动/噪声）
# 真实规律大概是：销售额 = 天数 * 1.5 + 5
np.random.seed(42) # 固定随机种子，确保你运行的结果和我一样
noise = np.random.normal(0, 1, size=len(days)) # 生成随机噪声
actual_sales = days * 1.5 + 5 + noise

# 3. 用 NumPy 的多项式拟合函数（polyfit）计算出趋势线的斜率和截距（底层最小二乘法算法）
slope, intercept = np.polyfit(days, actual_sales, 1)
trend_line = slope * days + intercept # 算出趋势线上的点

# 4. 用 Matplotlib 绘图呈现
plt.figure(figsize=(8, 5))

# 画出实际销售额的“散点图”
plt.scatter(days, actual_sales, color='blue', label='Actual Sales', s=100)
# 画出拟合的“趋势折线图”
plt.plot(days, trend_line, color='red', linestyle='--', linewidth=2, label='Trend Line')

# 美化图表
plt.title('Sales Trend Analysis', fontsize=14)
plt.xlabel('Days', fontsize=12)
plt.ylabel('Sales (K)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6) # 显示网格线
plt.legend() # 显示右上角的标签图例

# 渲染出来
plt.show()
```
### 📝 案例三：用户评论文本长度与情感分布（三剑客终极合体）
> 场景： 这是一个标准的 NLP 情感分析（Classification）的前置看板。我们要读取评论数据，统计文本长度，看看不同情感分类下的用户，说话的长短有什么规律。

```Python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 模拟读入一份社交媒体评论数据集
data = {
    'review': [
        'This product is amazing! Highly recommend it to everyone.',
        'Total waste of money, broke on the first day.',
        'It is okay, nothing special but works fine.',
        'Worst customer service ever! Extremely disappointed.',
        'Love it! Best purchase of the year.'
    ],
    'sentiment': ['Positive', 'Negative', 'Neutral', 'Negative', 'Positive']
}
df = pd.DataFrame(data)

# 2. 【Pandas 操作】类别分布统计：看正负面评论各有多少
print("--- 情感标签分布统计 ---")
print(df['sentiment'].value_counts())

# 3. 【Pandas + NumPy 操作】文本长度统计：新建一列长度特征
df['review_length'] = df['review'].str.len()

# 4. 【Pandas Groupby】分组统计：看看正面和负面评论，哪类人骂得更长/夸得更长？
avg_length = df.groupby('sentiment')['review_length'].mean()
print("\n--- 各类情感的平均评论字数 ---")
print(avg_length)

# 5. 【Matplotlib 操作】一键可视化对比
plt.figure(figsize=(6, 4))
# 画柱状图展示不同情感的平均评论长度
plt.bar(avg_length.index, avg_length.values, color=['red', 'gray', 'green'], alpha=0.8)

plt.title('Average Review Length by Sentiment')
plt.xlabel('Sentiment')
plt.ylabel('Average Number of Characters')
plt.show()
```