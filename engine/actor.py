# -*- coding: utf-8 -*-
"""
Actor Model implementation for ReaperOS.
Enables isolated concurrency and prevents Race Conditions via asynchronous message passing.
"""

import asyncio
from typing import Any, Dict, Optional

class ActorMessage:
    def __init__(self, sender: str, msg_type: str, payload: Any) -> None:
        self.sender = sender
        self.msg_type = msg_type
        self.payload = payload

class BaseActor:
    def __init__(self, name: str) -> None:
        self.name = name
        self.mailbox: asyncio.Queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        self.received_messages = []

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()

    async def send(self, recipient: 'BaseActor', msg_type: str, payload: Any) -> None:
        msg = ActorMessage(sender=self.name, msg_type=msg_type, payload=payload)
        await recipient.mailbox.put(msg)

    async def _loop(self) -> None:
        try:
            while True:
                msg = await self.mailbox.get()
                self.received_messages.append(msg)
                await self.receive(msg)
                self.mailbox.task_done()
        except asyncio.CancelledError:
            pass

    async def receive(self, message: ActorMessage) -> None:
        """Override this method in subclasses to process messages."""
        pass
