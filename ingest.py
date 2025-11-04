import os, json, subprocess, math, uuid
from pathlib import Path
from utils import ensure_dirs, embed_texts
import whisper

SNIPPETS_DIR = Path('media') / 'snippets'

def ffmpeg_extract_audio(video_path, out_audio):
    # requires ffmpeg installed on system
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', out_audio]
    subprocess.run(cmd, check=True)

def cut_snippet(video_path, start, duration, out_path):
    cmd = ['ffmpeg', '-y', '-ss', str(start), '-i', video_path, '-t', str(duration), '-c', 'copy', out_path]
    subprocess.run(cmd, check=True)

def transcribe_audio_whisper(audio_path, model_name='small'):
    model = whisper.load_model(model_name)
    res = model.transcribe(audio_path)
    # Whisper returns 'segments' with start/end and text in many builds
    segments = res.get('segments', [])
    return segments, res.get('text','')

def simple_segment_from_whisper(segments, max_len_sec=40):
    # segments: list of whisper segments with start,end,text
    # We'll merge small consecutive segments into up to max_len_sec chunks
    chunks = []
    current = None
    for seg in segments:
        s,e = seg['start'], seg['end']
        text = seg['text'].strip()
        if current is None:
            current = {'start': s, 'end': e, 'text': text}
        else:
            if (seg['end'] - current['start']) <= max_len_sec:
                current['end'] = e
                current['text'] = (current['text'] + ' ' + text).strip()
            else:
                chunks.append(current)
                current = {'start': s, 'end': e, 'text': text}
    if current is not None:
        chunks.append(current)
    return chunks

def process_upload_video(video_path, persona, snippets_out_dir='media/snippets'):
    ensure_dirs([snippets_out_dir])
    base = Path(video_path)
    audio_tmp = str(base.with_suffix('.wav'))
    ffmpeg_extract_audio(video_path, audio_tmp)
    # transcribe
    segments, full_text = transcribe_audio_whisper(audio_tmp, model_name='small')
    chunks = simple_segment_from_whisper(segments)
    # prepare snippets: cut video small mp4s and create metadata
    snippets_meta = []
    for i,ch in enumerate(chunks):
        sid = str(uuid.uuid4())[:8]
        start = ch['start']
        end = ch['end']
        duration = end - start
        snippet_fn = f"snippet_{sid}.mp4"
        out_snip = Path(snippets_out_dir) / snippet_fn
        # cut video (copy codec for speed). For more compatibility re-encode.
        cut_snippet(video_path, start, duration, str(out_snip))
        meta = {'id': sid, 'video_id': base.stem, 'start': start, 'end': end, 'duration': duration, 'transcript': ch['text'], 'snippet_file': snippet_fn, 'persona': persona}
        snippets_meta.append(meta)
    # cleanup audio_tmp
    try:
        os.remove(audio_tmp)
    except Exception:
        pass
    return snippets_meta
