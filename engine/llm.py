import asyncio
import numpy as np
import os
import json
from functools import lru_cache
from config import WEIGHTS_DIR, BASE_DIR

_LOCAL_EMBEDDER = None
_LOCAL_LLM = None
_LOCAL_TOKENIZER = None

@lru_cache(maxsize=1024)
def _cached_encode(text: str) -> list:
    global _LOCAL_EMBEDDER
    if _LOCAL_EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        model_path = os.path.join(WEIGHTS_DIR, "all-MiniLM-L6-v2")
        _LOCAL_EMBEDDER = SentenceTransformer(model_path, device='cpu')
    return _LOCAL_EMBEDDER.encode(text).tolist()

# Keep the embedder strictly local.
# It loads the sentence-transformer weights directly from the isolated local folder.
async def get_embedder_local(text):
    try:
        emb_list = await asyncio.to_thread(_cached_encode, text)
        return np.array(emb_list)
    except Exception as e:
        print(f"Local Embedding failed: {e}")
        return np.zeros(384)

async def generate_queries_local(query):
    """
    Agentic RAG Step 1: Query Expansion.
    Generates 3 variations of the query using the local Qwen model via MLX.
    """
    global _LOCAL_LLM, _LOCAL_TOKENIZER
    try:
        from mlx_lm import load, generate
        model_path = os.path.join(WEIGHTS_DIR, "Qwen2.5-0.5B-Instruct-4bit")
        
        # Simple prompt for the 0.5B model
        prompt = f"Generate 2 more specific search queries for: '{query}'. Return only the queries, one per line. No numbers."
        messages = [{"role": "user", "content": prompt}]
        
        if _LOCAL_LLM is None or _LOCAL_TOKENIZER is None:
            def _init_model():
                return load(model_path)
            _LOCAL_LLM, _LOCAL_TOKENIZER = await asyncio.to_thread(_init_model)
        
        # Generate in a thread to not block event loop
        def _infer():
            prompt_text = _LOCAL_TOKENIZER.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            response = generate(_LOCAL_LLM, _LOCAL_TOKENIZER, prompt=prompt_text, verbose=False, max_tokens=100)
            return response

        response = await asyncio.to_thread(_infer)
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        # Add original query and take top 3
        all_queries = [query] + queries
        return all_queries[:3]
    except Exception as e:
        print(f"Query expansion failed: {e}")
        return [query]
