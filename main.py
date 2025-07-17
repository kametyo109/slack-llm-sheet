# main.py

import os
import hmac
import hashlib
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime

import github_parser
import llm_parser
import sheets_logger

load_dotenv()

app = FastAPI()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")


@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")

    # Prevent replay attacks (allow max 5 min drift)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return JSONResponse(status_code=403, content={"error": "timestamp expired"})

    # Verify Slack signature
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, slack_signature):
        return JSONResponse(status_code=403, content={"error": "invalid signature"})

    # Process the Slack event
    payload = await request.json()
    event = payload.get("event", {})

    if event.get("type") == "app_mention":
        text = event.get("text", "")
        urls = [word for word in text.split() if word.startswith("http")]
        if urls:
            repo_url = urls[0]
            parsed = github_parser.parse_github_repo(repo_url)
            enriched = llm_parser.enrich_with_llm(parsed)
            enriched["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheets_logger.log_to_sheets(enriched)

        return {"status": "ok"}

    return {"status": "ignored"}


@app.post("/parse")
async def parse_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    urls = [word for word in text.split() if word.startswith("http")]
    if urls:
        repo_url = urls[0]
        parsed = github_parser.parse_github_repo(repo_url)
        enriched = llm_parser.enrich_with_llm(parsed)
        enriched["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheets_logger.log_to_sheets(enriched)
        return {"status": "logged", "data": enriched}
    return {"status": "no_url_found"}
