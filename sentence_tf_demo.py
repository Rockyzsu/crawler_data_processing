from sentence_transformers import SentenceTransformer, util


# 加载轻量级模型（适合CPU）
model = SentenceTransformer('./local-models/all-MiniLM-L6-v2')
def check():
    # 测试文本嵌入生成
    embedding = model.encode("Hello, world!")
    print(f"嵌入向量维度: {embedding.shape}")  # 应输出 (384,)


def sentance_bert():

    def text_similarity_bert(text1, text2):
        # 加载预训练模型（支持多语言）
        # model = SentenceTransformer('all-MiniLM-L6-v2')  # 轻量级模型，适合快速使用
        
        # 生成句子嵌入向量
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)
        
        # 计算余弦相似度
        cosine_score = util.cos_sim(embeddings1, embeddings2).item()
        return cosine_score

    # 示例
    text_a = "机器学习是人工智能的核心"
    text_b = "人工智能的核心是机器学习"
    text_c = "深度学习是机器学习的一个分支"

    print(f"A与B的相似度: {text_similarity_bert(text_a, text_b):.2f}")  # 约0.89（语义相似）
    print(f"A与C的相似度: {text_similarity_bert(text_a, text_c):.2f}")  # 约0.65（相关但不同）

if __name__ == "__main__":
    sentance_bert()