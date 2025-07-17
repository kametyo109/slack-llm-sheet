import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from llm_parser import enrich_slack_app
from sheets_logger import log_to_sheets

load_dotenv()

app = FastAPI()


class EnrichmentRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Slack App Enrichment Service is running.</h1>"


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

        if "slack.com/apps/" in text or "slack.com/marketplace/" in text or "github.com" in text:
            enriched = enrich_slack_app(text)
            if enriched:
                print(f"Enriched result: {enriched}")
                log_to_sheets(enriched)
            else:
                print("Enrichment failed or returned empty.")

    return {"status": "ok"}


@app.post("/enrich")
async def enrich(data: EnrichmentRequest):
    try:
        enriched = enrich_slack_app(data.text)
        if enriched:
            print(f"Enriched result: {enriched}")
            log_to_sheets(enriched)
            return {"status": "logged", "enriched": enriched}
        else:
            return {"status": "failed", "reason": "Empty result"}
    except Exception as e:
        print(f"Enrichment failed: {str(e)}")
        return {"status": "error", "detail": str(e)}
