import pytest
from unittest.mock import patch
from pydantic import ValidationError
from engine.vk_nexus import VKAuth, VKPublisher, VKScanner, VKListener

def test_vk_auth_initializes_without_token():
    with pytest.raises(ValidationError):
        VKAuth(token="")

def test_vk_auth_initializes_with_token():
    auth = VKAuth(token="fake_token_longer_than_10")
    assert auth.token == "fake_token_longer_than_10"

@patch('vk_api.VkApi')
def test_vk_publisher_formats_payload(mock_vk):
    auth = VKAuth(token="fake_token_longer_than_10")
    pub = VKPublisher(auth=auth)
    # We don't actually post, we test the logic payload builder
    payload = pub.build_post_payload(owner_id=-123, message="Test", from_group=1)
    
    assert payload['owner_id'] == -123
    assert payload['message'] == "Test"
    assert payload['from_group'] == 1

def test_vk_scanner_extracts_text():
    auth = VKAuth(token="fake_token_longer_than_10")
    scanner = VKScanner(auth=auth)
    fake_vk_response = {
        "items": [
            {"id": 1, "text": "Important news!", "likes": {"count": 10}},
            {"id": 2, "text": "Spam", "likes": {"count": 0}}
        ]
    }
    results = scanner.parse_posts(fake_vk_response, min_likes=5)
    assert len(results) == 1
    assert results[0]['text'] == "Important news!"

def test_vk_listener_handles_message():
    auth = VKAuth(token="fake_token_longer_than_10")
    listener = VKListener(auth=auth)
    
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
