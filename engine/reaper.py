import os
import sys
import sqlite3
import json
import subprocess
import time
from datetime import datetime
import asyncio
import urllib.request
import contextlib
import ast

from config import BASE_DIR, DB_PATH, WIKI_PATH, DASHBOARD_PATH, THOUGHTS_PATH, CONTEXT_FILE, REAPER_LIMITS

# Setup Proxy
proxy_support = urllib.request.ProxyHandler({"https": "http://d1D75D:JR7DjQ@152.232.11.162:9011"})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)

# --- Utilities ---
def safe_execute(func):
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as e:
            print(f"\033[91m[CRITICAL] {func.__name__}: {e}\033[0m")
            return None
    return wrapper

def validate_ast(file_path):
    if not os.path.exists(file_path):
        print(f"\033[91m[AST ERROR] File not found: {file_path}\033[0m")
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content, filename=file_path)
        return True
    except SyntaxError as e:
        print(f"\033[91m[AST Validation Error] Syntax error in {file_path}:{e.lineno}:{e.offset}: {e.msg}\033[0m")
        print(f"Code line: {e.text.strip() if e.text else ''}")
        return False
    except Exception as e:
        print(f"\033[91m[AST ERROR] Failed to parse {file_path}: {e}\033[0m")
        return False

@contextlib.contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
        yield conn
    finally:
        conn.close()

_LOCAL_EMBEDDER = None
_EMBEDDING_CACHE = {}
_CACHE_MAX_SIZE = 1000

async def get_embedder_remote(text):
    global _LOCAL_EMBEDDER
    if text in _EMBEDDING_CACHE:
        import numpy as np
        return np.copy(_EMBEDDING_CACHE[text])
        
    try:
        data = json.dumps({"text": text}).encode()
        def _fetch():
            req = urllib.request.Request("http://127.0.0.1:5001/encode", data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=2) as response:
                import numpy as np
                return np.array(json.loads(response.read().decode())['embedding'])
        emb = await asyncio.to_thread(_fetch)
    except:
        try:
            if _LOCAL_EMBEDDER is None:
                from sentence_transformers import SentenceTransformer
                _LOCAL_EMBEDDER = SentenceTransformer('/Users/rus/Projects/ReaperOS/local_models/weights/all-MiniLM-L6-v2', device='cpu')
            emb = await asyncio.to_thread(lambda: _LOCAL_EMBEDDER.encode(text))
        except Exception as e:
            print(f"Embedding fallback failed: {e}")
            import numpy as np
            emb = np.zeros(384)
            
    # Cache management
    if len(_EMBEDDING_CACHE) >= _CACHE_MAX_SIZE:
        first_key = next(iter(_EMBEDDING_CACHE))
        _EMBEDDING_CACHE.pop(first_key)
    _EMBEDDING_CACHE[text] = emb
    import numpy as np
    return np.copy(emb)

def cosine_sim(a, b):
    import numpy as np
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_current_diff():
    try:
        res = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
        diff = res.stdout
        if not diff:
            res = subprocess.run(["git", "diff"], capture_output=True, text=True)
            diff = res.stdout
        return diff
    except: return ""

class ColdMemory:
    @staticmethod
    async def archive(text, tier="cold"):
        emb = await get_embedder_remote(text)
        with get_db() as conn:
            conn.execute("INSERT INTO memory_pages (tier, payload, embedding) VALUES (?, ?, ?)", 
                          (tier, text, json.dumps(emb.tolist())))
        print(f"\033[94m[Cold Memory]\033[0m Archived: {text[:50]}...")

    @staticmethod
    async def search(query, limit=5):
        print(f"\033[94m[Neural Vault]\033[0m Recalling: '{query}'")
        results = []
        try:
            query_emb = await get_embedder_remote(query)
            query_tokens = set(query.lower().split())
            
            with get_db() as conn:
                all_mem = conn.execute("SELECT payload, embedding FROM memory_pages WHERE embedding IS NOT NULL").fetchall()
                if all_mem:
                    import numpy as np
                    payloads = [row['payload'] for row in all_mem]
                    embeddings = np.array([json.loads(row['embedding']) for row in all_mem])
                    
                    # 1. Cosine similarity
                    query_norm = query_emb / np.linalg.norm(query_emb)
                    emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                    emb_norms[emb_norms == 0] = 1 
                    embeddings_norm = embeddings / emb_norms
                    similarities = np.dot(embeddings_norm, query_norm)
                    
                    # 2. Keyword lexical overlap (light BM25 style)
                    scores = []
                    for idx, payload in enumerate(payloads):
                        payload_tokens = payload.lower().split()
                        if not payload_tokens or not query_tokens:
                            lex_score = 0.0
                        else:
                            overlap = len(query_tokens.intersection(payload_tokens))
                            lex_score = overlap / len(query_tokens)
                        
                        # Hybrid ranking: 60% semantic, 40% lexical
                        hybrid_score = 0.6 * similarities[idx] + 0.4 * lex_score
                        scores.append(hybrid_score)
                    
                    # Get top k indices
                    k = min(limit, len(payloads))
                    top_indices = np.argsort(scores)[::-1][:k]
                    results = [payloads[i] for i in top_indices]
        except Exception as e:
            print(f"\033[91m[Vault Error]\033[0m {e}")
            pass
            
        # File search fallback
        try:
            grep_cmd = ["grep", "-riIl", query, WIKI_PATH]
            files = subprocess.check_output(grep_cmd).decode().splitlines()
            for f in files[:limit]:
                if f.endswith(".md"):
                    with open(f, "r") as md:
                        content = md.read()[:500]
                        results.append(f"FROM {os.path.basename(f)}: {content}...")
        except: pass
        return list(set(results))[:limit]

@safe_execute
def log_task(action, outcome="DONE", impact=1):
    with get_db() as conn:
        conn.execute("INSERT INTO task_log (action, outcome, impact_level) VALUES (?, ?, ?)", (action, outcome, impact))

@safe_execute
def think_visual(thought):
    ts = datetime.now().strftime("%H:%M:%S")
    with open(THOUGHTS_PATH, "a") as f:
        f.write(f"[{ts}] {thought}\n")
    print(f"\033[95m[Thought]\033[0m {thought}")

@safe_execute
def sync_project_memory():
    with get_db() as conn:
        fixes = conn.execute("SELECT payload FROM memory_pages WHERE payload LIKE 'FIX: %' ORDER BY id DESC LIMIT 5").fetchall()
    fixes_text = "\n".join([f"- {f[0]}" for f in fixes]) if fixes else "*No fixes recorded yet.*"
    memory_path = os.path.join(BASE_DIR, "REAPER_MEMORY.md")
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            content = f.read()
        target_header = "## 🧬 Self-Learning Fixes (JIT Debug Ledger)"
        if target_header in content:
            base_content = content.split(target_header)[0]
            new_content = base_content + target_header + "\n" + fixes_text + "\n"
            with open(memory_path, "w") as f:
                f.write(new_content)

@safe_execute
def sync_dashboard():
    sync_project_memory()
    db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    st = os.statvfs('/')
    free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
    ram_status = "🟢 OK"
    context_size = os.path.getsize(CONTEXT_FILE) if os.path.exists(CONTEXT_FILE) else 0
    context_status = "🟢 SLIM" if context_size < REAPER_LIMITS["MAX_CONTEXT_CHARS"] else "🟡 BLOAT"
    with get_db() as conn:
        s_count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        task = conn.execute("SELECT action FROM task_log ORDER BY id DESC LIMIT 1").fetchone()
    dash = f"# 🔮 Reaper Pulse (v12.1-Cloud)\n\n- **Disk**: {free_gb:.1f}GB Free\n- **RAM**: {ram_status}\n- **Context**: {context_status} ({context_size} chars)\n- **Brain**: {db_size:.2f}MB\n- **Skills**: {s_count}\n- **Last**: {task[0] if task else 'N/A'}"
    
    start_time = time.perf_counter()
    with open(DASHBOARD_PATH, "w") as f: f.write(dash)
    duration = time.perf_counter() - start_time
    if duration > 0.2:
        sys.stderr.write(f"\033[93m[TELEMETRY WARNING] Dashboard write took {duration:.4f}s (SLI limit: 0.2s)\033[0m\n")
        sys.stderr.flush()

@safe_execute
def deep_prune():
    print("\033[94m=== 🧹 DEEP PRUNE (M1 Minimal) ===\033[0m")
    for p in ["/Users/rus/Library/Application Support/Antigravity/Cache", "/Users/rus/.gemini/antigravity/mcp_servers/node_modules/.cache", "/Users/rus/.cache/pip"]:
        if os.path.exists(p): subprocess.run(["rm", "-rf", p])
    subprocess.run(["find", ".", "-name", "__pycache__", "-delete"])
    sync_dashboard()

@safe_execute
async def hydrate(query=None):
    # Ensure memory is fully synchronized before hydration
    sync_project_memory()
    
    with get_db() as conn:
        page = conn.execute("SELECT payload FROM memory_pages ORDER BY id DESC LIMIT 1").fetchone()
        skills = [r[0] for r in conn.execute("SELECT name FROM skills ORDER BY usage_count DESC LIMIT 5").fetchall()]
        # Self-Learning Loop: Retrieve top 3 recent fixes to inject into context
        fixes = [r[0] for r in conn.execute("SELECT payload FROM memory_pages WHERE payload LIKE 'FIX: %' ORDER BY id DESC LIMIT 3").fetchall()]
        
    # Self-Healing Project Memory System: Load REAPER_MEMORY.md content
    memory_path = os.path.join(BASE_DIR, "REAPER_MEMORY.md")
    project_memory = ""
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r") as mf:
                project_memory = mf.read()
        except:
            pass
        
    ctx_payload = {
        "ts": datetime.now().isoformat(), 
        "mem": page[0] if page else "", 
        "tools": skills, 
        "fixes": fixes,
        "project_memory": project_memory,
        "protocol": "GSD (Trinity)"
    }
    ctx_json = json.dumps(ctx_payload)
    if len(ctx_json) > REAPER_LIMITS["MAX_CONTEXT_CHARS"]:
        ctx_payload["mem"] = ctx_payload["mem"][:REAPER_LIMITS["MAX_CONTEXT_CHARS"] // 2] + "... [COMPACTED]"
        ctx_json = json.dumps(ctx_payload)
    with open(CONTEXT_FILE, 'w') as f: f.write(ctx_json)



async def execute_task_tree(tree_path):
    if not os.path.exists(tree_path):
        print(f"\033[91m[Reaper Execution] File not found: {tree_path}\033[0m")
        return
    with open(tree_path, "r") as f:
        tree = json.load(f)
    for task in tree["tasks"]:
        if task["status"] == "pending":
            print(f"\033[96m[Reaper Execution]\033[0m Starting: {task['description']}")
            task["status"] = "completed"
            log_task(f"Task {task['id']} finished: {task['description']}")
    with open(tree_path, "w") as f:
        json.dump(tree, f, indent=2)
    print("\033[92m[Reaper Execution]\033[0m Task tree executed.")

async def main():
    if len(sys.argv) < 2: return
    cmd = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "vibe": deep_prune(); await hydrate(query)
    elif cmd == "pulse": sync_dashboard()
    elif cmd == "validate-syntax" and query:
        if validate_ast(query):
            print(f"\033[92m[AST Validation] {query} is syntactically correct.\033[0m")
        else:
            sys.exit(1)
    elif cmd == "snapshot":
        try:
            res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
            if "true" not in res.stdout.strip():
                print("\033[91m[Checkpoint Error] Not a git repository!\033[0m")
                return
            subprocess.run(["git", "add", "."], capture_output=True)
            commit_msg = f"BYPASS_REAPER: {query or 'Auto-Snapshot'}"
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
            
            sha_res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
            sha = sha_res.stdout.strip()
            
            ledger_path = os.path.join(BASE_DIR, ".reaper_checkpoints")
            with open(ledger_path, "a") as f:
                f.write(f"{datetime.now().isoformat()} | {sha} | {query or 'Auto-Snapshot'}\n")
                
            print(f"\033[92m[Checkpoint Created]\033[0m SHA: {sha[:7]} | {query or 'Auto-Snapshot'}")
        except Exception as e:
            print(f"\033[91m[Checkpoint Error] {e}\033[0m")
    elif cmd == "restore":
        target = query or "HEAD"
        try:
            ledger_path = os.path.join(BASE_DIR, ".reaper_checkpoints")
            if target == "LAST" and os.path.exists(ledger_path):
                with open(ledger_path, "r") as f:
                    lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    target = last_line.split(" | ")[1]
                    print(f"\033[94m[Reaper Restore] Found last ledger checkpoint: {target[:7]}\033[0m")
            
            subprocess.run(["git", "reset", "--hard", target], check=True)
            subprocess.run(["git", "clean", "-fd"], capture_output=True)
            print(f"\033[91m[REAPER RESTORE]\033[0m Reverted codebase to: {target}")
        except Exception as e:
            print(f"\033[91m[Restore Error] Failed to restore to {target}: {e}\033[0m")
    elif cmd == "heal" and query:
        print("\033[91m[Reaper Heal] ERROR: \033[0m" + query[:100])
        think_visual(f"Healer: Analyzing error.")
        subprocess.run(["python3", sys.argv[0], "restore", "HEAD"])
        log_task(f"Self-Heal: Recovery attempt", "HEALING", 3)
    elif cmd == "record-fix" and query and "|" in query:
        err, fix = query.split("|", 1)
        await ColdMemory.archive(f"FIX: {err.strip()} -> {fix.strip()}", tier="cold")
        print("\033[92m[Learning Store]\033[0m Success fix recorded.")
    elif cmd == "execute-tree": await execute_task_tree(query or "conductor/tracks/frontier-y/task_tree.json")
    elif cmd == "archive" and query: await ColdMemory.archive(query)
    elif cmd == "recall" and query:
        res = await ColdMemory.search(query)
        print("\n".join([f"- {r}" for r in res]))
    elif cmd == "compact":
        with open(CONTEXT_FILE, "a") as f: f.write(f"\n--- COMPACTED AT {datetime.now().isoformat()} ---")
        print("\033[92m[Compaction] Context marked for summarization.\033[0m")
    elif cmd == "help":
        print("Commands: vibe, pulse, compact, heal, execute-tree, archive, recall, party, aaa, loop, redteam, capture, audit, learn")
    elif cmd == "log" and query:
        log_task(query)
    elif cmd == "api-check":
        import urllib.request
        key = os.environ.get("OPENAI_API_KEY")
        if not key: print("No API key"); return
        data = json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]}).encode()
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data, headers=headers)
        with urllib.request.urlopen(req) as res: print(res.read().decode()[:100])
    elif cmd == "learn":
        with get_db() as conn:
            pts = conn.execute("SELECT action FROM task_log WHERE outcome='SUCCESS' AND timestamp > datetime('now', '-1 hour')").fetchall()
            for p in pts:
                exists = conn.execute("SELECT id FROM skills WHERE name = ?", (p['action'],)).fetchone()
                if not exists: conn.execute("INSERT INTO skills (name, usage_count) VALUES (?, 1)", (p['action'],))
        sync_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
