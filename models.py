from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    text: str
    chat_id: Optional[str] = None
