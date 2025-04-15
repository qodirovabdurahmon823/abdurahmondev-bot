import json
import uuid
from pathlib import Path

CHAT_DIR = Path("chat_data")
CHAT_DIR.mkdir(exist_ok=True)

def get_chat_history(chat_id: str) -> list:
    file = CHAT_DIR / f"chat_{chat_id}.json"
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(chat_id: str, history: list):
    file = CHAT_DIR / f"chat_{chat_id}.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def create_chat_id() -> str:
    return str(uuid.uuid4())
