# 构建corpus 语料库，里面的每一个词是一个token
corpus = [
    "I love this movie, it is an amazing masterpiece!",
    "I hate this film, the plot is terrible and boring.",
    "This movie is mediocre, neither good nor bad.",
    "I love this movie!",
    "I love this film but hate the plot."
]


#//////////////////////////////////////////////////////////////////////////////////////////////////
# #token化这个语料库
# tokenized_corpus = [sentence.lower().split(" ") for sentence in corpus]
# print("分词token化的结果：\n", tokenized_corpus)

# #构建词汇表vocubulary
# vocab = set()
# for tokens in tokenized_corpus:
#     vocab.update(tokens)

# vocab = sorted(list(vocab))
# print("长度：\n", len(vocab))
# print("内容： \n", vocab)
#/////////////////////////////////////////////////////////////////////////////////////////////////////

# #n-gram :
# import nltk
# from nltk.util import ngrams

# # 1. 原始文本
# text = "artificial intelligence is the future"
# tokens = text.split()

# # 2. 生成 Bigram (n=2) 和 Trigram (n=3)
# bi_grams = list(ngrams(tokens, 2))
# tri_grams = list(ngrams(tokens, 3))

# print("【Bigram 结果】:", bi_grams)
# print("【Trigram 结果】:", tri_grams)


#///////////////////////////////////////////////////////////////////////////////////////////////


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
# One-Hot（独热编码）： 它是最根本的离散表征方式。如果词汇表有 V 个词，每个词都会变成一个长度为 V 的向量，只有该词对应索引的位置为 1，其余全为 0。
# Bag of Words（词袋模型）： 忽略文本的语法和语序，把文本看作一个装词的“袋子”。一句话的 BoW 向量，就是这句话中所有词的 One-Hot 向量的累加。
#                            在这个箱子里，句子的词序、语法、句式通通被丢弃，计算机只关心一个问题：每个词在句子里出现了几次？
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(corpus)

feature_names = vectorizer.get_feature_names_out()

df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

print("特征总数 (包含N-gram):\n", len(feature_names))
print("\n部分特征示例:\n", feature_names)

print("\n每个文本的 TF-IDF 详细数值表：\n",df_tfidf)