# VK Autopilot (VK Nexus) Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a unified, portable VK integration module (`vk_nexus.py`) for Reaper OS that handles automated posting, parsing, DM assistance, and community management.

**Architecture:** We use a Hybrid architecture. The core logic is completely decoupled from the transport layer (LongPoll/API calls), meaning the exact same functions can later be triggered by an n8n webhook or a VPS cron job. We will use the official `vk_api` python library. The system is split into three core classes: `VKPublisher`, `VKScanner`, and `VKListener`.

**Tech Stack:** Python 3.12, `vk_api`, `pytest` (for TDD).

---

### Task 1: Environment & Authentication Setup

**Files:**
- Create: `engine/vk_nexus.py`
- Modify: `engine/config.py` (assumed to exist or we create it)
- Test: `tests/test_vk_nexus.py`

**Step 1: Write the failing test**
```python
# tests/test_vk_nexus.py
import pytest
from engine.vk_nexus import VKAuth

def test_vk_auth_initializes_without_token():
    with pytest.raises(ValueError):
        VKAuth(token=None)

def test_vk_auth_initializes_with_token():
    auth = VKAuth(token="fake_token")
    assert auth.token == "fake_token"
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_vk_nexus.py::test_vk_auth_initializes_without_token -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'engine.vk_nexus'"

**Step 3: Write minimal implementation**
```python
# engine/vk_nexus.py
class VKAuth:
    def __init__(self, token: str):
        if not token:
            raise ValueError("VK Token is required")
        self.token = token
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_vk_nexus.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/test_vk_nexus.py engine/vk_nexus.py
git commit -m "feat(vk): implement base VKAuth class"
```

---

### Task 2: The Publisher (Auto-Posting)

**Files:**
- Modify: `engine/vk_nexus.py`
- Modify: `tests/test_vk_nexus.py`

**Step 1: Write the failing test**
```python
# tests/test_vk_nexus.py
from engine.vk_nexus import VKPublisher, VKAuth
from unittest.mock import patch

@patch('vk_api.VkApi')
def test_vk_publisher_formats_payload(mock_vk):
    auth = VKAuth("fake")
    pub = VKPublisher(auth)
    # We don't actually post, we test the logic payload builder
    payload = pub.build_post_payload(owner_id=-123, message="Test", from_group=1)
    
    assert payload['owner_id'] == -123
    assert payload['message'] == "Test"
    assert payload['from_group'] == 1
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_vk_nexus.py::test_vk_publisher_formats_payload -v`
Expected: FAIL with "ImportError: cannot import name 'VKPublisher'"

**Step 3: Write minimal implementation**
```python
# engine/vk_nexus.py
import vk_api

class VKPublisher:
    def __init__(self, auth: VKAuth):
        self.auth = auth
        # In a real scenario, this connects to VK. For tests, we mock it.
        # self.session = vk_api.VkApi(token=self.auth.token)
        # self.api = self.session.get_api()

    def build_post_payload(self, owner_id: int, message: str, from_group: int = 1) -> dict:
        return {
            "owner_id": owner_id,
            "message": message,
            "from_group": from_group
        }
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_vk_nexus.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/vk_nexus.py tests/test_vk_nexus.py
git commit -m "feat(vk): implement VKPublisher payload builder"
```

---

### Task 3: The Scanner (Parsing Competitors)

**Files:**
- Modify: `engine/vk_nexus.py`
- Modify: `tests/test_vk_nexus.py`

**Step 1: Write the failing test**
```python
# tests/test_vk_nexus.py
from engine.vk_nexus import VKScanner

def test_vk_scanner_extracts_text():
    scanner = VKScanner(VKAuth("fake"))
    fake_vk_response = {
        "items": [
            {"id": 1, "text": "Important news!", "likes": {"count": 10}},
            {"id": 2, "text": "Spam", "likes": {"count": 0}}
        ]
    }
    results = scanner.parse_posts(fake_vk_response, min_likes=5)
    assert len(results) == 1
    assert results[0]['text'] == "Important news!"
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_vk_nexus.py::test_vk_scanner_extracts_text -v`
Expected: FAIL with "ImportError: cannot import name 'VKScanner'"

**Step 3: Write minimal implementation**
```python
# engine/vk_nexus.py
class VKScanner:
    def __init__(self, auth: VKAuth):
        self.auth = auth

    def parse_posts(self, raw_response: dict, min_likes: int = 0) -> list:
        results = []
        for item in raw_response.get('items', []):
            if item.get('likes', {}).get('count', 0) >= min_likes:
                results.append({
                    "id": item.get("id"),
                    "text": item.get("text", "")
                })
        return results
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_vk_nexus.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/vk_nexus.py tests/test_vk_nexus.py
git commit -m "feat(vk): implement VKScanner for parsing with filters"
```

---

### Task 4: The Listener (DM & Comm Mgmt Logic)

*Note: We test the logic of handling an incoming message, completely independent of how it arrived (LongPoll or Webhook).*

**Files:**
- Modify: `engine/vk_nexus.py`
- Modify: `tests/test_vk_nexus.py`

**Step 1: Write the failing test**
```python
# tests/test_vk_nexus.py
from engine.vk_nexus import VKListener

def test_vk_listener_handles_message():
    listener = VKListener(VKAuth("fake"))
    
    # Simulate an incoming webhook payload or longpoll event
    fake_event = {
        "type": "message_new",
        "object": {
            "message": {
                "from_id": 12345,
                "text": "Hello bot"
            }
        }
    }
    
    action = listener.process_event(fake_event)
    assert action['type'] == 'reply'
    assert action['user_id'] == 12345
    assert action['intent'] == 'handle_dm'
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_vk_nexus.py::test_vk_listener_handles_message -v`
Expected: FAIL with "ImportError: cannot import name 'VKListener'"

**Step 3: Write minimal implementation**
```python
# engine/vk_nexus.py
class VKListener:
    def __init__(self, auth: VKAuth):
        self.auth = auth

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
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_vk_nexus.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/vk_nexus.py tests/test_vk_nexus.py
git commit -m "feat(vk): implement VKListener event processor"
```
