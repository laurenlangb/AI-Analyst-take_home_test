from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.database import fetch_offers


class ChatRequest(BaseModel):
    message: str


# Shown in the chat answer box before the user asks anything, and for blank questions.
CHAT_PLACEHOLDER = "Ask a question about the offers data."

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Render the main data table page.
@app.get("/", response_class=HTMLResponse)
def data_table(request: Request):
    return templates.TemplateResponse(
        "data_table.html", {"request": request, "chat_placeholder": CHAT_PLACEHOLDER}
    )

# Return offer data as JSON for the frontend table.
@app.get("/api/data")
def get_data():
    return {"data": fetch_offers()}


@app.post("/api/chat")
def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        return {"answer": CHAT_PLACEHOLDER}

    return {"answer": f"connected: {question}"}
