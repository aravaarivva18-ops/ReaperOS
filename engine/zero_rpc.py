# -*- coding: utf-8 -*-
"""
Zero RPC Engine for ReaperOS.
Fast, typed, socket-based Remote Procedure Call (RPC) system using Pydantic.
"""

import socket
import json
import threading
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel

class RPCRequest(BaseModel):
    method: str
    params: Dict[str, Any]

class RPCResponse(BaseModel):
    result: Optional[Any] = None
    error: Optional[str] = None

class ZeroRPCServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 4242) -> None:
        self.host = host
        self.port = port
        self.methods: Dict[str, Callable[..., Any]] = {}
        self.running = False
        self._server_socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None

    def register_method(self, name: str, func: Callable[..., Any]) -> None:
        self.methods[name] = func

    def start(self) -> None:
        self.running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._server_socket:
            try:
                # Trigger shutdown via self-connection or closing
                self._server_socket.close()
            except Exception:
                pass

    def _listen_loop(self) -> None:
        while self.running:
            try:
                conn, addr = self._server_socket.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
                client_thread.start()
            except Exception:
                break

    def _handle_client(self, conn: socket.socket) -> None:
        with conn:
            try:
                data = conn.recv(65536)
                if not data:
                    return
                req_dict = json.loads(data.decode())
                req = RPCRequest(**req_dict)
                
                if req.method in self.methods:
                    result = self.methods[req.method](**req.params)
                    resp = RPCResponse(result=result)
                else:
                    resp = RPCResponse(error=f"Method not found: {req.method}")
            except Exception as e:
                resp = RPCResponse(error=str(e))
                
            try:
                conn.sendall(json.dumps(resp.model_dump()).encode())
            except Exception:
                pass

class ZeroRPCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 4242) -> None:
        self.host = host
        self.port = port

    def call(self, method: str, params: Dict[str, Any]) -> Any:
        req = RPCRequest(method=method, params=params)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json.dumps(req.model_dump()).encode())
            
            # Read response
            chunks = []
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            data = b"".join(chunks)
            
            resp_dict = json.loads(data.decode())
            resp = RPCResponse(**resp_dict)
            
            if resp.error:
                raise RuntimeError(f"RPC Error: {resp.error}")
            return resp.result
