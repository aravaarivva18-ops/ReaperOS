import os
import sys
import json
import sqlite3
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import DB_PATH, BASE_DIR

app = Flask(__name__)
CORS(app)

# Add parent dir to path so we can import engine modules
sys.path.append(BASE_DIR)
from reaper import ColdMemory

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Dashboard template not found.", 404

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
    app.run(host='127.0.0.1', port=8234)
