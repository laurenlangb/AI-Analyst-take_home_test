from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.auth import (
    COOKIE_NAME,
    SESSION_HOURS,
    check_credentials,
    create_token,
    get_current_user,
    require_user,
)
from app.database import fetch_offers
from app.gemini import generate_sql


class ChatRequest(BaseModel):
    message: str


# Shown in the chat answer box before the user asks anything, and for blank questions.
CHAT_PLACEHOLDER = "Ask a question about the offers data."

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/")
def root():
    # /dashboard redirects on to /login when there is no valid session.
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if get_current_user(request) is not None:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "data_table.html",
        {
            "request": request,
            "chat_placeholder": CHAT_PLACEHOLDER,
            "user_name": user["name"],
        },
    )



@app.post("/api/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if not check_credentials(email, password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password."},
            status_code=401,
        )

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        create_token(),
        httponly=True,
        samesite="lax",
        max_age=SESSION_HOURS * 3600,
    )
    return response



@app.get("/api/data", dependencies=[Depends(require_user)])
def get_data():
    return {"data": fetch_offers()}


@app.post("/api/chat", dependencies=[Depends(require_user)])
def chat(payload: ChatRequest):
    question = payload.message.strip()
    if not question:
        return {"answer": CHAT_PLACEHOLDER}
    # Gemini turns the question into SQL. 
    sql = generate_sql(question)
    return {"answer": f"Generated SQL: {sql}"}
