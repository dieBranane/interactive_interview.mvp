from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()

# Ordner für statische Dateien
if not os.path.exists("static"):
    os.makedirs("static")

# Ordner für hochgeladene Videos
VIDEO_DIR = "static/videos"
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# Templates Ordner
if not os.path.exists("templates"):
    os.makedirs("templates")

templates = Jinja2Templates(directory="templates")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    videos = os.listdir(VIDEO_DIR)
    videos = [f"/static/videos/{v}" for v in videos]
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos})

@app.post("/upload", response_class=HTMLResponse)
async def upload_video(request: Request, file: UploadFile = File(...)):
    video_path = os.path.join(VIDEO_DIR, file.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    videos = os.listdir(VIDEO_DIR)
    videos = [f"/static/videos/{v}" for v in videos]
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos, "message": f"{file.filename} hochgeladen!"})
