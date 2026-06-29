import pandas as pd
import html
import re

df = pd.read_csv("datasets/all_jobs.csv")

def clean_text(text):
    if pd.isna(text): return ""
    text = str(text)
    # decode html entities multiple times (some are double encoded)
    for _ in range(3):
        text = html.unescape(text)
    # remove html tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # remove leftover html artifacts
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#?\w+;', ' ', text)
    # remove unicode junk like \u1160
    text = re.sub(r'[\u1100-\u11ff\uffa0-\uffdc]', '', text)
    # collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df["description"] = df["description"].apply(clean_text)
df["title"] = df["title"].apply(clean_text)
df["location"] = df["location"].apply(clean_text)
df = df[df["title"].str.len() > 0]
df = df[df["description"].str.len() > 0]
df = df.drop_duplicates(subset=["title", "apply_url"])
df = df.fillna("")
df.to_csv("datasets/all_jobs.csv", index=False)
print(f"Cleaned. Rows: {len(df)}")
print("\nSample description:")
print(df["description"].iloc[0][:300])