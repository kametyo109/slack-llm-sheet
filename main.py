import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from sheets_logger import log_to_sheets
from llm_parser import summarize_webpage  # Use OpenAI

load_dotenv()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Slack Link Logger is running.</h1>"

@app.post("/slack/events")
async def slack_events(request: Request):
    payload = await request.json()

    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    event = payload.get("event", {})
    text = event.get("text", "")
    user = event.get("user", "")
    ts = event.get("ts", "")
    print(f"[Slack] Received event: {text} from {user} at {ts}")

    for word in text.split():
        cleaned = word.strip("<>")
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
