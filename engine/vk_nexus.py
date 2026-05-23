from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any

class VKAuth(BaseModel):
    token: str = Field(..., min_length=10, description="VK API access token")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("VK Token cannot be whitespace only")
        return v

class VKPostPayload(BaseModel):
    owner_id: int = Field(..., description="ID of the user or community page owner")
    message: str = Field(..., min_length=1, description="Post text message")
    from_group: int = Field(1, ge=0, le=1, description="1 if post is from group, 0 if from user")

class VKPublisher(BaseModel):
    auth: VKAuth

    def build_post_payload(self, owner_id: int, message: str, from_group: int = 1) -> dict:
        payload = VKPostPayload(owner_id=owner_id, message=message, from_group=from_group)
        return payload.model_dump()

class VKPostItem(BaseModel):
    id: int
    text: str = ""

class VKScanner(BaseModel):
    auth: VKAuth

    def parse_posts(self, raw_response: dict, min_likes: int = 0) -> List[Dict[str, Any]]:
        results = []
        items = raw_response.get('items', [])
        for item in items:
            likes_count = item.get('likes', {}).get('count', 0)
            if likes_count >= min_likes:
                post = VKPostItem(
                    id=item.get("id"),
                    text=item.get("text", "")
                )
                results.append(post.model_dump())
        return results

class VKListener(BaseModel):
    auth: VKAuth

    def process_event(self, event_data: dict) -> dict:
        if event_data.get("type") == "message_new":
            msg = event_data.get("object", {}).get("message", {})
            return {
                "type": "reply",
                "user_id": msg.get("from_id"),
                "intent": "handle_dm",
                "original_text": msg.get("text")
            }
        return {"type": "ignore"}
