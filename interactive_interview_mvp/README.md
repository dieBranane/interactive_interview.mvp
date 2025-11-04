# Interactive Interview MVP

Dieses Repository enthält ein lauffähiges Prototype-MVP für ein interaktives Interview-System ähnlich der USC "Dimensions in Testimony" Methodik. 
Ziel: Frage eingeben → bestpassendes echtes Video-Snippet abspielen.

## Enthaltene Dateien
- `app.py` : FastAPI Backend mit Endpoints `/ingest` (Upload Video), `/ask` (Textfrage)
- `ingest.py` : Hilfsskript zur Transkription (Whisper), Segmentierung und Vorverarbeitung
- `utils.py` : Embeddings (sentence-transformers) + FAISS Index Funktionen
- `frontend.html` : Minimaler Web-Client zum Fragen stellen und Snippet abspielen
- `requirements.txt` : Python-Abhängigkeiten
- `Dockerfile` : Optional für Containerisierung

## Voraussetzungen
- Python 3.9+
- ffmpeg auf dem System installiert (für Audio/Video Verarbeitung)
- Empfehlenswert: GPU für Whisper (optional); ansonsten langsamer CPU-Modus.

## Schnellstart (lokal)
1. Virtuelle Umgebung erstellen:
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Server starten:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
3. WebUI öffnen: `http://localhost:8000/frontend`

## Workflow
1. `/ingest` - upload eines Videos (mp4). Das Skript extrahiert Audio, transkribiert (Whisper), splittet in Snippets, erzeugt Embeddings und baut FAISS Index auf.
2. `/ask` - POST mit JSON `{ "query": "..." }` → Antwort: bestpassendes snippet metadata `{ video_id, start, end, transcript, snippet_file }`
3. Client spielt das Snippet ab (vorverarbeitete mp4 snippet-files werden erzeugt).

## Hinweise & Ethik
- Dieses Projekt ist ein MVP-Prototype. Für Produktion sind weitere Schritte nötig (Re-Ranker, bessere Segmentierung, Authentifizierung, Consent-Management).
- Nutze stets schriftliche Einwilligung der interviewten Personen.

