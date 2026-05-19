from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import fetch_offers

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Render the main data table page.
@app.get("/", response_class=HTMLResponse)
def data_table(request: Request):
    return templates.TemplateResponse("data_table.html", {"request": request})

# Return offer data as JSON for the frontend table.
@app.get("/api/data")
def get_data():
    return {"data": fetch_offers()}

