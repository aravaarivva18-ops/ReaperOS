import os
import sys
import json
import sqlite3
import asyncio
import subprocess
import random
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import DB_PATH, BASE_DIR

# Initialize Flask to serve static files directly from dashboard/
app = Flask(__name__, static_folder='../dashboard', static_url_path='')
CORS(app)

# Add parent dir to path so we can import engine/tools modules
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'tools'))
from reaper import ColdMemory

model_path = os.path.join(BASE_DIR, 'local_models', 'weights', 'all-MiniLM-L6-v2')
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        if os.path.exists(model_path):
            model = SentenceTransformer(model_path)
        else:
            model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn

def is_process_running(pattern):
    try:
        output = subprocess.check_output(["pgrep", "-f", pattern])
        return 1 if output.strip() else 0
    except Exception:
        return 0

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health():
    import time
    return jsonify({'status': 'healthy', 'time': time.time()})

@app.route('/encode', methods=['POST'])
def encode():
    import time
    from knowledge_brain import add_telemetry
    start_time = time.time()
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400
        
    try:
        m = get_model()
        emb = m.encode(data['text'])
        latency_ms = (time.time() - start_time) * 1000
        
        # Пишем телеметрию
        add_telemetry("encode_latency", latency_ms, f"Text length: {len(data['text'])}")
        
        # SLI предупреждение в логи при задержке >500ms
        if latency_ms > 500:
            print(f"⚠️ [WARNING] SLI Breach: encode_latency = {latency_ms:.1f}ms (>500ms)")
            add_telemetry("sli_warning", latency_ms, "encode_latency > 500ms")
            
        return jsonify({'embedding': emb.tolist(), 'latency_ms': latency_ms})
    except Exception as e:
        add_telemetry("encode_error", 1.0, str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    try:
        from knowledge_brain import get_latest_telemetry
        metric_name = request.args.get('metric', 'encode_latency')
        telemetry_data = get_latest_telemetry(metric_name=metric_name, limit=20)
        if telemetry_data:
            # Map database keys if necessary (ui expects {"value": val})
            mapped_data = []
            for row in telemetry_data:
                mapped_data.append({
                    "value": row.get("value", 0),
                    "timestamp": row.get("timestamp"),
                    "details": row.get("details")
                })
            return jsonify({'status': 'success', 'data': mapped_data})
    except Exception as e:
        print(f"Error reading telemetry: {e}")
        
    # Fallback to dummy data if DB is empty or fails
    latency_values = [
        {"value": random.randint(80, 140)},
        {"value": random.randint(90, 160)},
        {"value": random.randint(70, 130)},
        {"value": random.randint(150, 240)},
        {"value": random.randint(80, 150)},
        {"value": random.randint(110, 220)},
        {"value": random.randint(90, 140)}
    ]
    return jsonify({
        "status": "success",
        "data": latency_values
    })

@app.route('/api/status', methods=['GET'])
def get_process_status():
    try:
        from knowledge_brain import get_process_status as db_get_process_status
        status_data = db_get_process_status()
        if status_data:
            # map keys if necessary
            mapped_status = []
            for proc in status_data:
                mapped_status.append({
                    "process_name": proc.get("process_name"),
                    "is_alive": proc.get("is_alive", 0),
                    "restarts_count": proc.get("restarts_count", 0),
                    "timestamp": proc.get("timestamp")
                })
            return jsonify({'status': 'success', 'data': mapped_status})
    except Exception as e:
        print(f"Error reading process status: {e}")

    # Fallback to dynamic pgrep status check
    daemon_running = is_process_running("engine.daemon")
    orchestrator_running = is_process_running("engine.main start")
    
    return jsonify({
        "status": "success",
        "data": [
            {
                "process_name": "embedder_server",
                "is_alive": daemon_running
            },
            {
                "process_name": "conductor",
                "is_alive": orchestrator_running
            }
        ]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        # Get count
        node_count = conn.execute("SELECT COUNT(*) FROM memory_pages").fetchone()[0]
        
        # Get recent memories
        mem_rows = conn.execute(
            "SELECT id, tier, payload, timestamp FROM memory_pages ORDER BY id DESC LIMIT 10"
        ).fetchall()
        recent_memories = [dict(row) for row in mem_rows]
        
        # Get health logs
        health_rows = conn.execute(
            "SELECT timestamp, metric_name, value, status FROM system_health ORDER BY id DESC LIMIT 10"
        ).fetchall()
        health_logs = [dict(row) for row in health_rows]
        
        conn.close()
        return jsonify({
            "node_count": node_count,
            "recent_memories": recent_memories,
            "health_logs": health_logs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def semantic_query():
    data = request.json or {}
    query = data.get('query', '').strip()
    if not query:
        return jsonify({"status": "error", "message": "Empty query"}), 400
    
    try:
        # Run async search in synchronous Flask context
        results = asyncio.run(ColdMemory.search(query, limit=5))
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_mcp_setup():
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    python_path = sys.executable
    mcp_config = {
        "command": python_path,
        "args": ["-m", "engine.mcp_server"],
        "env": {
            "PYTHONPATH": f"{project_root}:{project_root}/engine"
        }
    }
    
    configs_updated = []
    
    # 1. Claude Desktop Config
    claude_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    if os.path.exists(os.path.dirname(claude_path)):
        try:
            data = {}
            if os.path.exists(claude_path):
                with open(claude_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if "mcpServers" not in data:
                data["mcpServers"] = {}
            data["mcpServers"]["reaper-os"] = mcp_config
            with open(claude_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            configs_updated.append("Claude Desktop")
        except Exception as e:
            sys.stderr.write(f"Failed to update Claude configuration: {e}\n")

    # 2. Cursor Config
    cursor_path = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/moose.json")
    if os.path.exists(os.path.dirname(cursor_path)):
        try:
            data = {}
            if os.path.exists(cursor_path):
                with open(cursor_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if "mcpServers" not in data:
                data["mcpServers"] = {}
            data["mcpServers"]["reaper-os"] = mcp_config
            with open(cursor_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            configs_updated.append("Cursor")
        except Exception as e:
            sys.stderr.write(f"Failed to update Cursor configuration: {e}\n")

    # 3. Windsurf Config
    windsurf_path = os.path.expanduser("~/.codeium/windsurf/mcp_config.json")
    if os.path.exists(os.path.dirname(windsurf_path)):
        try:
            data = {}
            if os.path.exists(windsurf_path):
                with open(windsurf_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if "mcpServers" not in data:
                data["mcpServers"] = {}
            data["mcpServers"]["reaper-os"] = mcp_config
            with open(windsurf_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            configs_updated.append("Windsurf")
        except Exception as e:
            sys.stderr.write(f"Failed to update Windsurf configuration: {e}\n")

    if configs_updated:
        return True, f"Successfully registered in: {', '.join(configs_updated)}"
    return False, "No compatible IDE folders found to configure."

@app.route('/api/setup', methods=['POST'])
def setup_mcp():
    success, msg = run_mcp_setup()
    if success:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400

if __name__ == '__main__':
    # Start on port 5001 as required by the OLED dashboard configuration
    app.run(host='0.0.0.0', port=5001)
