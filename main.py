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

    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    event = payload.get("event", {})
    text = event.get("text", "")
    user = event.get("user", "")
    ts = event.get("ts", "")
    print(f"[Slack] Received event: {text} from {user} at {ts}")

    for word in text.split():
        print(f"[Debug] Checking word: {word}")
        if word.startswith("http://") or word.startswith("https://"):
            print(f"[Slack] Detected link: {word}")
            try:
                log_to_sheets(link=word)
                print("[Slack] log_to_sheets() called successfully.")
            except Exception as e:
                print(f"[Slack] Error while calling log_to_sheets(): {e}")

    return {"status": "ok"}
