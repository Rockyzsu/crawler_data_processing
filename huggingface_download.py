from huggingface_hub import hf_hub_download, snapshot_download

# 示例1：下载单个文件（如模型权重文件）
# 下载 "bert-base-uncased" 模型的 config.json 到当前目录
# hf_hub_download(
#     repo_id="bert-base-uncased",  # 模型/数据集仓库ID（格式：用户名/仓库名）
#     filename="config.json",       # 要下载的文件名
#     local_dir="./bert-model"      # 本地保存目录（可选）
# )

# 示例2：下载整个模型仓库（推荐）
# 下载 "sentence-transformers/all-MiniLM-L6-v2" 完整模型到本地
model_dir = snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    local_dir="./local-models/all-MiniLM-L6-v2"  # 本地保存路径
)
print(f"模型已保存到：{model_dir}")