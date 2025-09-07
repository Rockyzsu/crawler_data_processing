from sentence_transformers import SentenceTransformer

# 加载轻量级模型（适合CPU）
model = SentenceTransformer('all-MiniLM-L6-v2')

# 测试文本嵌入生成
embedding = model.encode("Hello, world!")
print(f"嵌入向量维度: {embedding.shape}")  # 应输出 (384,)