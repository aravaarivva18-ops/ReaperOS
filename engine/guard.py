# Guard Policy: Whitelist of allowed tool execution patterns
ALLOWED_PATTERNS = [
    "encode",
    "log",
    "pulse",
    "start",
    "setup",
    "dashboard"
]

def check_permission(cmd: str):
    if cmd not in ALLOWED_PATTERNS:
        print(f"\033[91m[Security Veto]\033[0m Command {cmd} blocked.")
        return False
    return True
