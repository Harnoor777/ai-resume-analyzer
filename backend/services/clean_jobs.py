import pandas as pd
import html
import re

df = pd.read_csv("datasets/all_jobs.csv")

def clean_text(text):
    if pd.isna(text): return ""
    text = html.unescape(str(text))
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df["description"] = df["description"].apply(clean_text)
df["title"] = df["title"].apply(clean_text)
df["location"] = df["location"].apply(clean_text)

# drop rows with empty title or description
df = df[df["title"].str.len() > 0]
df = df[df["description"].str.len() > 0]

# drop duplicates
df = df.drop_duplicates(subset=["title", "apply_url"])

# fill nulls
df = df.fillna("")

df.to_csv("datasets/all_jobs.csv", index=False)
print(f"Cleaned. Rows: {len(df)}")
print(df["description"].iloc[0][:300])