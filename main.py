import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from sheets_logger import log_to_sheets
from llm_parser import summarize_webpage

load_dotenv()

app = FastAPI()
recent_ts = set()  # Cache of processed timestamps to prevent duplicate logging

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Slack Link Logger is running.</h1>"

@app.post("/slack/events")
async def slack_events(request: Request):
    payload = await request.json()

    # Handle Slack URL verification
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    event = payload.get("event", {})
    text = event.get("text", "")
    user = event.get("user", "")
    ts = event.get("ts", "")

    print(f"[Slack] Received event: {text} from {user} at {ts}")

    # ✅ Deduplicate Slack events by timestamp
    if ts in recent_ts:
        print(f"[Slack] Duplicate event detected (ts: {ts}) — skipping.")
        return {"status": "duplicate_skipped"}
    recent_ts.add(ts)

    for word in text.split():
        # Strip Slack link formatting and Slack's display alias
        cleaned = word.strip("<>").split("|")[0]
        print(f"[Debug] Checking word: {cleaned}")
        if cleaned.startswith("http://") or cleaned.startswith("https://"):
            print(f"[Slack] Detected link: {cleaned}")
            try:
                summary = summarize_webpage(cleaned)
                title = summary.get("title", "N/A")
                description = summary.get("description", "N/A")

                log_to_sheets({
                    "title": title,
                    "description": description,
                    "link": cleaned
                })
                print("[Slack] log_to_sheets() called successfully.")
            except Exception as e:
                print(f"[Slack] Error while calling log_to_sheets(): {e}")

    return {"status": "ok"}
