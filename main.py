import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from llm_parser import enrich_repository
from sheets_logger import log_to_sheets

load_dotenv()

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Slack Enrichment App is running.</h1>"


@app.post("/slack/events")
async def slack_events(request: Request):
    payload = await request.json()

    # Slack URL verification challenge
    if "type" in payload and payload["type"] == "url_verification":
        return {"challenge": payload["challenge"]}

    # Handle events
    if "event" in payload:
        event = payload["event"]
        text = event.get("text", "")
        user = event.get("user", "")
        ts = event.get("ts", "")
        print(f"Received event: {text} from {user} at {ts}")

        if "http" in text and "@" in text:
            enriched = enrich_repository(text)
            if enriched:
                print(f"Enriched result: {enriched}")
                log_to_sheets(enriched)
            else:
                print("Enrichment failed or returned empty.")

    return {"status": "ok"}
