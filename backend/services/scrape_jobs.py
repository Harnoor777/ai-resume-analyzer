import asyncio, json, sys, csv, os
from urllib.parse import urljoin
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "https://job-boards.greenhouse.io/linear"
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "all_jobs.csv")
CSV_FIELDS = ["title","location","department","employment_type","experience","description","apply_url","posted_date","company","source_url"]

def load_seen():
    seen = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                seen.add((row.get("title",""), row.get("apply_url","")))
    return seen

def save_jobs(jobs, source_url, company):
    exists = os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for j in jobs:
            j["company"] = company
            j["source_url"] = source_url
            w.writerow(j)

def parse_jobs(data, base="", seen=set()):
    found = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and any(k in item for k in ["title","job_title","name","position","text"]):
                locs = item.get("locations") or []
                cats = item.get("categories") or {}
                loc = item.get("location") or item.get("office") or \
                      (locs[0] if locs and isinstance(locs[0], str) else \
                      (locs[0].get("name","") if locs else "")) or \
                      (cats.get("location","") if isinstance(cats, dict) else "")
                key = (item.get("title") or item.get("text",""), item.get("absolute_url") or item.get("hostedUrl") or item.get("applyUrl",""))
                if key in seen: continue
                seen.add(key)
                found.append({
                    "title": item.get("title") or item.get("text") or item.get("name") or item.get("position",""),
                    "location": loc,
                    "department": item.get("department") or item.get("team") or (cats.get("department","") if isinstance(cats, dict) else ""),
                    "employment_type": item.get("employment_type") or item.get("type") or (cats.get("commitment","") if isinstance(cats, dict) else ""),
                    "experience": item.get("experience") or item.get("seniority") or (cats.get("level","") if isinstance(cats, dict) else ""),
                    "description": item.get("description") or item.get("content") or item.get("descriptionPlain",""),
                    "apply_url": item.get("absolute_url") or item.get("hostedUrl") or item.get("applyUrl") or item.get("url") or (urljoin(base, item.get("relative_url","")) if item.get("relative_url") else ""),
                    "posted_date": item.get("posted_date") or item.get("createdAt") or item.get("created_at",""),
                })
            else:
                found.extend(parse_jobs(item, base, seen))
    elif isinstance(data, dict):
        for v in data.values():
            if isinstance(v, (list, dict)):
                found.extend(parse_jobs(v, base, seen))
    return found

async def fetch_api(ctx, url):
    try:
        r = await ctx.request.get(url, headers={"Accept":"application/json"})
        if r.ok: return await r.json()
    except: pass
    return None

async def scrape():
    host = TARGET.split("//")[-1].split("/")[0]
    slug = TARGET.rstrip("/").split("/")[-1]
    seen = load_seen()
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()

        if "lever.co" in host:
            data = await fetch_api(ctx, f"https://api.lever.co/v0/postings/{slug}?mode=json")
            if data: jobs = parse_jobs(data, TARGET, seen)

        elif "greenhouse.io" in host or "greenhouse" in TARGET:
            data = await fetch_api(ctx, f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
            if data: jobs = parse_jobs(data, TARGET, seen)

        elif "ashbyhq.com" in host:
            data = await fetch_api(ctx, f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
            if data: jobs = parse_jobs(data, TARGET, seen)

        elif "workable.com" in host:
            data = await fetch_api(ctx, f"https://apply.workable.com/api/v3/accounts/{slug}/jobs")
            if data: jobs = parse_jobs(data, TARGET, seen)

        else:
            # Playwright fallback for unknown platforms
            page = await ctx.new_page()
            intercepted = []
            async def on_resp(r):
                if "json" in r.headers.get("content-type",""):
                    try: intercepted.append(await r.json())
                    except: pass
            page.on("response", on_resp)
            await page.goto(TARGET, wait_until="networkidle", timeout=30000)
            for body in intercepted:
                jobs.extend(parse_jobs(body, TARGET, seen))

        await browser.close()

    if jobs:
        save_jobs(jobs, TARGET, slug)
        print(f"[OK] {len(jobs)} new jobs saved to datasets/all_jobs.csv")
    else:
        print("[NONE] No new jobs found (all duplicates or empty response)")

    print(json.dumps({"company": slug, "source_url": TARGET, "new_jobs": len(jobs)}, indent=2))

asyncio.run(scrape())