import pytest
import asyncio
from engine.actor import BaseActor, ActorMessage

class PingActor(BaseActor):
    async def receive(self, message: ActorMessage) -> None:
        if message.msg_type == "ping":
            await self.send(message.payload["reply_to"], "pong", {"reply_from": self})

class PongActor(BaseActor):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.pong_received = False

    async def receive(self, message: ActorMessage) -> None:
        if message.msg_type == "pong":
            self.pong_received = True

@pytest.mark.anyio
async def test_actor_ping_pong():
    ping = PingActor("Ping")
    pong = PongActor("Pong")
    
    ping.start()
    pong.start()
    
    # Trigger message flow
    await pong.send(ping, "ping", {"reply_to": pong})
    
    # Wait for the actors to process
    await asyncio.sleep(0.1)
    
    assert pong.pong_received is True
    
    ping.stop()
    pong.stop()
