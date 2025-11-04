import os, json, glob
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle

EMB_MODEL_NAME = 'all-mpnet-base-v2'

def ensure_dirs(paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

# load embedding model (singleton pattern)
_emb_model = None
def get_embedding_model():
    global _emb_model
    if _emb_model is None:
        _emb_model = SentenceTransformer(EMB_MODEL_NAME)
    return _emb_model

def embed_texts(texts):
    model = get_embedding_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.astype('float32')

# Index helpers - simple FAISS IndexFlatL2
def build_index_from_snippets(snippets_meta, index_dir='index_data'):
    Path(index_dir).mkdir(parents=True, exist_ok=True)
    texts = [s['transcript'] for s in snippets_meta]
    ids = [s['id'] for s in snippets_meta]
    vectors = embed_texts(texts)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    # save index and metadata
    faiss.write_index(index, os.path.join(index_dir, 'faiss.index'))
    with open(os.path.join(index_dir, 'meta.pkl'), 'wb') as f:
        pickle.dump({'ids': ids, 'snippets': snippets_meta}, f)
    return True

def load_index_metadata(index_dir='index_data'):
    import pickle
    with open(os.path.join(index_dir, 'meta.pkl'), 'rb') as f:
        meta = pickle.load(f)
    index = faiss.read_index(os.path.join(index_dir, 'faiss.index'))
    return index, meta

def query_index(query, top_k=10, index_dir='index_data'):
    index, meta = load_index_metadata(index_dir)
    q_vec = embed_texts([query])
    D, I = index.search(q_vec, top_k)
    ids = meta['ids']
    snippets = meta['snippets']
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(snippets): continue
        s = snippets[idx].copy()
        s['score'] = float(score)
        results.append(s)
    return results
