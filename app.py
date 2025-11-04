import os
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
import shutil
import uuid
from pathlib import Path
from utils import ensure_dirs, build_index_from_snippets, query_index, load_index_metadata
from ingest import process_upload_video

MEDIA_DIR = Path('media')
SNIPPETS_DIR = MEDIA_DIR / 'snippets'
VIDEOS_DIR = MEDIA_DIR / 'videos'
INDEX_DIR = Path('index_data')

ensure_dirs([MEDIA_DIR, SNIPPETS_DIR, VIDEOS_DIR, INDEX_DIR])

app = FastAPI(title='Interactive Interview MVP')

@app.post('/ingest')
async def ingest(video: UploadFile = File(...), persona: str = Form('persona_1')):
    # save uploaded video
    vid_id = str(uuid.uuid4())[:8]
    out_path = VIDEOS_DIR / f"{vid_id}.mp4"
    with open(out_path, 'wb') as f:
        shutil.copyfileobj(video.file, f)
    # process (transcribe, segment, embed, create snippets)
    snippets_meta = process_upload_video(str(out_path), persona, snippets_out_dir=str(SNIPPETS_DIR))
    # build index
    build_index_from_snippets(snippets_meta, index_dir=str(INDEX_DIR))
    return JSONResponse({'status':'ok', 'video_id': vid_id, 'num_snippets': len(snippets_meta), 'snippets_preview': snippets_meta[:5]})

class AskRequest(BaseModel):
    query: str
    k: int = 10

@app.post('/ask')
async def ask(req: AskRequest):
    results = query_index(req.query, top_k=req.k, index_dir=str(INDEX_DIR))
    # return best hit + snippet file path (relative)
    if len(results)==0:
        return JSONResponse({'status': 'no_match'})
    best = results[0]
    # path to snippet mp4
    snippet_file = best.get('snippet_file')
    return JSONResponse({'status':'ok', 'best': best})

@app.get('/snippet/{filename}')
async def get_snippet(filename: str):
    path = SNIPPETS_DIR / filename
    if not path.exists():
        return JSONResponse({'error': 'not found'}, status_code=404)
    return FileResponse(path)

@app.get('/frontend')
async def frontend():
    return HTMLResponse(open('frontend.html','r', encoding='utf-8').read())

@app.get('/health')
async def health():
    return JSONResponse({'status':'ok'})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)
