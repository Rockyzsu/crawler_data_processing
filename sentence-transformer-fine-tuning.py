from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation, util
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import random

# ----------------------
# 1. 自定义数据集（映射式数据集）
# ----------------------
class CustomDataset(Dataset):
    def __init__(self, examples):
        self.examples = examples
        
    def __len__(self):
        return len(self.examples)
        
    def __getitem__(self, idx):
        return self.examples[idx]

# 准备数据
data = [
    {"sentence1": "人工智能正在改变世界", "sentence2": "AI技术对全球产生深远影响", "score": 0.92},
    {"sentence1": "我喜欢用Python编程", "sentence2": "我热爱使用Python编写代码", "score": 0.88},
    {"sentence1": "北京是中国的首都", "sentence2": "上海是中国的经济中心", "score": 0.23},
    {"sentence1": "今天天气真好", "sentence2": "今天天气很不错", "score": 0.85},
    {"sentence1": "机器学习是人工智能的分支", "sentence2": "深度学习属于机器学习领域", "score": 0.76},
]

df = pd.DataFrame(data)

# 构建训练样本并打乱
train_examples = [
    InputExample(
        texts=[row["sentence1"], row["sentence2"]],
        label=row["score"]
    ) for _, row in df.iterrows()
]
random.shuffle(train_examples)

# 使用自定义数据集
train_dataset = CustomDataset(train_examples)
train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=2)

# ----------------------
# 2. 加载基础模型
# ----------------------
model = SentenceTransformer("./local-models/uer/sbert-base-chinese-nli")

# ----------------------
# 3. 配置训练参数
# ----------------------
train_loss = losses.CosineSimilarityLoss(model)

evaluator = evaluation.EmbeddingSimilarityEvaluator(
    sentences1=df["sentence1"].tolist(),
    sentences2=df["sentence2"].tolist(),
    scores=df["score"].tolist(),
    name="train-eval"
)

num_epochs = 10
warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
output_path = "./local-models/fine-tuned-model"

# ----------------------
# 4. 执行训练
# ----------------------
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=num_epochs,
    warmup_steps=warmup_steps,
    output_path=output_path,
    show_progress_bar=True,
    evaluation_steps=5
)

# ----------------------
# 5. 测试微调后的模型（修复余弦相似度计算）
# ----------------------
fine_tuned_model = SentenceTransformer(output_path)

sentence1 = "自然语言处理是人工智能的重要领域"
sentence2 = "NLP是AI的关键分支"
embedding1 = fine_tuned_model.encode(sentence1, convert_to_tensor=True)
embedding2 = fine_tuned_model.encode(sentence2, convert_to_tensor=True)

# 关键修复：使用util.cos_sim而非losses.CosineSimilarityLoss.cos_sim
similarity = util.cos_sim(embedding1, embedding2).item()

print(f"微调后模型计算的相似度: {similarity:.4f}")
    