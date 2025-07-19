import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from sheets_logger import log_to_sheets

load_dotenv()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Slack Link Logger is running.</h1>"

@app.post("/slack/events")
async def slack_events(request: Request):
    payload = await request.json()

    # Handle Slack URL verification (first-time setup)
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # Handle Slack message events
    event = payload.get("event", {})
    text = event.get("text", "")
    user = event.get("user", "")
    ts = event.get("ts", "")
    print(f"[Slack] Received event: {text} from {user} at {ts}")

    # Extract and clean any URLs
    for word in text.split():
        cleaned = word.strip("<>")
        print(f"[Debug] Checking word: {cleaned}")
        if cleaned.startswith("http://") or cleaned.startswith("https://"):
            print(f"[Slack] Detected link: {cleaned}")
            try:
                log_to_sheets(link=cleaned)
                print("[Slack] log_to_sheets() called successfully.")
            except Exception as e:
                print(f"[Slack] Error while calling log_to_sheets(): {e}")

    return {"status": "ok"}
