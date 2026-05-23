import os
import sys
import socket
import json
import asyncio
import signal
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

from config import BASE_DIR, SOCKET_PATH

READY_FILE = os.path.join(BASE_DIR, ".daemon_ready")
MODEL_PATH = os.path.join(BASE_DIR, "local_models/weights/all-MiniLM-L6-v2")

# Global thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=2)

async def handle_request(reader, writer):
    data = await reader.read(8192)
    try:
        request = json.loads(data.decode())
        if request.get("cmd") == "encode":
            loop = asyncio.get_running_loop()
            # Offload heavy ML to executor
            emb = await loop.run_in_executor(executor, model.encode, request["text"])
            response = {"embedding": emb.tolist()}
        else:
            response = {"error": "Unknown command"}
    except Exception as e:
        response = {"error": str(e)}
    
    writer.write(json.dumps(response).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def run_daemon():
    global model
    print("Daemon: Loading model...")
    model = SentenceTransformer(MODEL_PATH, device='cpu')
    
    # Register signal handlers for clean shutdown
    loop = asyncio.get_running_loop()
    def shutdown_handler():
        print("Daemon: Shutdown signal received. Cleaning up...")
        for task in asyncio.all_tasks(loop):
            task.cancel()
            
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)
    
    if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
    
    server = await asyncio.start_unix_server(handle_request, path=SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o777)
    with open(READY_FILE, "w") as f: f.write("ready")
    
    print(f"Daemon: Listening on {SOCKET_PATH}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(run_daemon())
    except asyncio.CancelledError:
        print("Daemon: Tasks cancelled cleanly.")
    finally:
        if os.path.exists(READY_FILE): os.remove(READY_FILE)
        if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
