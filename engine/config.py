import os

# Helper to find and load .env file
def load_dotenv():
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        os.environ.setdefault(k, v)
            break

load_dotenv()

BASE_DIR = os.path.abspath(os.path.expanduser(os.getenv("REAPER_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
WIKI_PATH = os.path.abspath(os.path.expanduser(os.getenv("REAPER_WIKI_PATH", os.path.expanduser("~/Documents/Knowledge-Brain"))))
DB_PATH = os.path.abspath(os.path.expanduser(os.getenv("REAPER_DB_PATH", os.path.join(WIKI_PATH, "db.sqlite"))))
SOCKET_PATH = os.path.abspath(os.path.expanduser(os.getenv("REAPER_SOCKET_PATH", os.path.join(BASE_DIR, "engine.sock"))))
DASHBOARD_PATH = os.path.abspath(os.path.expanduser(os.getenv("REAPER_DASHBOARD_PATH", os.path.join(WIKI_PATH, "Dashboard.md"))))
THOUGHTS_PATH = os.path.abspath(os.path.expanduser(os.getenv("REAPER_THOUGHTS_PATH", os.path.join(WIKI_PATH, "THOUGHTS.md"))))
CONTEXT_FILE = os.path.abspath(os.path.expanduser(os.getenv("REAPER_CONTEXT_FILE", os.path.join(BASE_DIR, ".reaper_context"))))
WEIGHTS_DIR = os.path.abspath(os.path.expanduser(os.getenv("REAPER_WEIGHTS_DIR", os.path.join(BASE_DIR, "local_models/weights"))))

STITCH_API_KEY = os.getenv("STITCH_API_KEY")

VK_CONFIG = {
    "USER_TOKEN": os.getenv("VK_USER_TOKEN"),
    "GROUP_TOKEN": os.getenv("VK_GROUP_TOKEN"),
    "GROUP_ID": os.getenv("VK_GROUP_ID")
}

REAPER_LIMITS = {
    "MAX_CONTEXT_CHARS": 8000,
    "THINKING_TOKEN_CAP": 10000,
    "COMPACT_THRESHOLD_PCT": 50
}

MCP_SERVERS = {
    "sequential-thinking": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"],
    "github": ["npx", "-y", "@modelcontextprotocol/server-github"],
    "browser": ["npx", "-y", "onestep-puppeteer-mcp-server"],
    "filesystem": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "--args", WIKI_PATH]
}

