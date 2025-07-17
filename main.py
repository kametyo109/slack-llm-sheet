import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv
from sheets_logger import log_to_sheets
from github_parser import parse_github_repo
from llm_parser import enrich_repository

load_dotenv()

ENRICHMENT_API_URL = os.getenv("ENRICHMENT_API_URL")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Slack GitHub Logger is live!"}

@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.json()

    # Echo challenge for Slack URL verification
    if "challenge" in body:
        return JSONResponse(content={"challenge": body["challenge"]})

    try:
        event = body.get("event", {})
        text = event.get("text", "")
        user = event.get("user", "")
        ts = event.get("ts", "")

        print(f"Received event: {text} from {user} at {ts}")

        async with httpx.AsyncClient() as client:
            response = await client.post(ENRICHMENT_API_URL, json={"text": text})

        if response.status_code == 200:
            enriched = response.json()
            print(f"Enriched result: {enriched}")
            log_to_sheets(enriched)
        else:
            print(f"Enrichment failed: {response.text}")

    except Exception as e:
        print(f"Error handling Slack event: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return JSONResponse(status_code=200, content={"ok": True})
