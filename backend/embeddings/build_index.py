import os, json
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR   = os.path.join(os.path.dirname(__file__), "..", "..")
JOBS_PATH  = os.path.join(BASE_DIR, "datasets", "all_jobs.csv")
INDEX_PATH = os.path.join(BASE_DIR, "datasets", "faiss_index.bin")
META_PATH  = os.path.join(BASE_DIR, "datasets", "faiss_meta.json")

print("Loading jobs...")
df = pd.read_csv(JOBS_PATH).fillna("")
texts = (df["description"] + " " + df["title"]).tolist()
meta  = df[["title","company","location","apply_url"]].to_dict("records")

print(f"Encoding {len(texts)} jobs (this runs once)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
embeddings = embeddings.astype(np.float32)

# normalize for cosine similarity
faiss.normalize_L2(embeddings)

print("Building FAISS index...")
dim   = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)  # inner product = cosine after normalization
index.add(embeddings)

print(f"Saving index ({index.ntotal} vectors)...")
faiss.write_index(index, INDEX_PATH)
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(meta, f)

print(f"Done! Index saved to datasets/faiss_index.bin")
print(f"Meta saved to datasets/faiss_meta.json")