import os
from huggingface_hub import snapshot_download

def download_models():
    base_dir = "/Users/rus/Projects/ReaperOS/local_models/weights"
    os.makedirs(base_dir, exist_ok=True)
    
    print("Downloading Qwen2.5-0.5B-Instruct-4bit for MLX...")
    qwen_dir = os.path.join(base_dir, "Qwen2.5-0.5B-Instruct-4bit")
    snapshot_download(
        repo_id="mlx-community/Qwen2.5-0.5B-Instruct-4bit",
        local_dir=qwen_dir,
        local_dir_use_symlinks=False
    )
    
    print("Downloading all-MiniLM-L6-v2 for Embeddings...")
    minilm_dir = os.path.join(base_dir, "all-MiniLM-L6-v2")
    snapshot_download(
        repo_id="sentence-transformers/all-MiniLM-L6-v2",
        local_dir=minilm_dir,
        local_dir_use_symlinks=False
    )
    
    print(f"All weights successfully isolated in {base_dir}")

if __name__ == "__main__":
    download_models()
