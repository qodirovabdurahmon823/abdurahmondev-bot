from fastapi import FastAPI, HTTPException, Body
from openai import OpenAI
from models import ChatRequest
from chat_manager import get_chat_history, save_chat_history, create_chat_id
from config import API_TOKEN, BASE_URL, MODEL_NAME, MAX_TOKENS
from pathlib import Path
from middlewares import add_middlewares  # ✅ Import it

app = FastAPI()
add_middlewares(app)

client = OpenAI(api_key=API_TOKEN, base_url=BASE_URL)

PROMPT_PATH = Path("prompts/default_prompt.txt")

def load_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    else:
        return "System prompt not found."

@app.post("/chat/create/")
async def create_new_chat(initial_message: str = Body(..., embed=True)):
    chat_id = create_chat_id()
    history = [
        {"role": "system", "content": load_system_prompt()},
        {"role": "user", "content": initial_message}
    ]
    save_chat_history(chat_id, history)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
            max_tokens=MAX_TOKENS
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        save_chat_history(chat_id, history)
        return {"chat_id": chat_id, "response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat(req: ChatRequest):
    if not req.chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")

    history = get_chat_history(req.chat_id)
    if not history:
        raise HTTPException(status_code=404, detail="Chat ID not found")

    history.append({"role": "user", "content": req.text})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
            max_tokens=MAX_TOKENS,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        save_chat_history(req.chat_id, history)
        return {"chat_id": req.chat_id, "response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{chat_id}")
async def get_history(chat_id: str):
    history = get_chat_history(chat_id)
    if not history:
        raise HTTPException(status_code=404, detail="Chat ID not found")
    return history

@app.get("/prompt/")
async def get_prompt():
    return {"content": load_system_prompt()}
