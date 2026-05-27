#!/usr/bin/env python3
import requests
import json
import time
import os
from datetime import datetime, timedelta

# API Token
TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjYwMzAydjEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjEsImVudCI6MSwiZXhwIjoxNzk1NTYwNjgyLCJpZCI6IjAxOWU2M2U5LTFjODAtNzdjNC1iZjQyLTAzZDQ5YTc3NDJjYSIsImlpZCI6NjYwOTQxMDUsIm9pZCI6NjcwNzMzLCJzIjoxMDczNzQxODYyLCJzaWQiOiJhYTBmM2U0My02MmY5LTQ3MTctYjJlYS1kMzc0NWY4ZTU1YTAiLCJ0IjpmYWxzZSwidWlkIjo2NjA5NDEwNX0.n345qDykS6AXVZwiX91SpcK8emANCoUqkEOzoy5ABnxT5yXzMVdoWE9vks0AfpftTfRFpfihLFOKV_ZNo1-6Fw"

# Dynamic scratch path calculation
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.getenv("SCRATCH_DIR")
if not SCRATCH_DIR:
    SCRATCH_DIR = os.path.join(project_root, "scratch")

os.makedirs(SCRATCH_DIR, exist_ok=True)

CARDS_FILE = os.path.join(SCRATCH_DIR, "cards.json")
STOCKS_FILE = os.path.join(SCRATCH_DIR, "stocks.json")
ORDERS_FILE = os.path.join(SCRATCH_DIR, "orders.json")

def api_request(method, url, headers, json_body=None, params=None):
    retries = 5
    delay = 5
    for attempt in range(retries):
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=json_body, headers=headers, params=params, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"[429] Rate limit hit. Sleeping {delay}s (Attempt {attempt+1}/{retries})...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Exception during request: {e}")
            time.sleep(delay)
            delay *= 2
    return None

def fetch_cards():
    print("Fetching product cards...")
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    
    cards = []
    cursor = {"limit": 100}
    
    while True:
        payload = {
            "settings": {
                "cursor": cursor,
                "filter": {"withPhoto": -1}
            }
        }
        
        data = api_request("POST", url, headers, json_body=payload)
        if not data or 'cards' not in data:
            break
            
        batch = data['cards']
        if not batch:
            break
            
        cards.extend(batch)
        print(f"Fetched {len(batch)} cards (Total: {len(cards)})")
        
        # Check if cursor is returned in the response
        resp_cursor = data.get('cursor')
        if not resp_cursor or len(batch) < 100:
            break
            
        cursor = resp_cursor
        time.sleep(0.5) # Anti-ban delay
        
    # Write to file
    with open(CARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cards)} cards to {CARDS_FILE}")
    return cards

def fetch_stocks():
    print("Fetching stocks...")
    url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    params = {
        "dateFrom": "2026-01-01T00:00:00"
    }
    
    data = api_request("GET", url, headers, params=params)
    if data is None:
        data = []
        
    with open(STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} stocks records to {STOCKS_FILE}")
    return data

def fetch_orders():
    print("Fetching orders...")
    url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    # Calculate 30 days ago
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
    params = {
        "dateFrom": date_from
    }
    
    data = api_request("GET", url, headers, params=params)
    if data is None:
        data = []
        
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} orders records to {ORDERS_FILE}")
    return data

def main():
    print("Starting Wildberries Extractor...")
    fetch_cards()
    fetch_stocks()
    fetch_orders()
    print("All extractions completed.")

if __name__ == "__main__":
    main()
