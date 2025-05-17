from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_lang(request: Request):
    lang = request.query_params.get("lang", "en").lower()
    if lang not in ["en", "ru", "de"]:
        lang = "en"
    return lang

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    lang = get_lang(request)
    return templates.TemplateResponse(f"index.{lang}.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    lang = get_lang(request)
    return templates.TemplateResponse(f"about.{lang}.html", {"request": request})

@app.get("/pay", response_class=HTMLResponse)
async def pay(request: Request):
    lang = get_lang(request)
    return templates.TemplateResponse(f"pay.{lang}.html", {"request": request})