from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import hashlib
import hmac
import os
import json
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Environment Variables ===
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
ENRICHMENT_API_URL = os.getenv("ENRICHMENT_API_URL", "https://slack-llm-sheet.onrender.com/enrich")
SHEET_NAME = os.getenv("SHEET_NAME", "LLM_Slack_Metadata")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")  # JSON string

# === FastAPI App ===
app = FastAPI()


# === Slack Signature Verification ===
def verify_slack_signature(slack_signature, timestamp, body):
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    sig_basestring = f"v0:{timestamp}:{body}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)


# === Google Sheets Client ===
def get_sheet_client():
    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


# === Slack Events Endpoint ===
@app.post("/slack/events")
async def slack_events(
    request: Request,
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None)
):
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")

    # Verification challenge
    try:
        data = json.loads(body_str)
    except:
        return JSONResponse(status_code=400, content={"error": "invalid json"})

    if data.get("type") == "url_verification":
        return JSONResponse(content={"challenge": data["challenge"]})

    # Signature check
    if not verify_slack_signature(x_slack_signature, x_slack_request_timestamp, body_str):
        return JSONResponse(status_code=403, content={"error": "invalid signature"})

    # Handle app mention events
    event = data.get("event", {})
    if event.get("type") == "app_mention":
        text = event.get("text", "")
        user = event.get("user", "")
        ts = event.get("ts", "")
        print(f"Received mention: {text} from {user} at {ts}")

        # Enrich
        async with httpx.AsyncClient() as client:
            response = await client.post(ENRICHMENT_API_URL, json={"text": text})
            if response.status_code == 200:
                result = response.json()
                enriched = result.get("enriched_metadata", {})
                enriched["input"] = text
                enriched["user"] = user
                enriched["timestamp"] = ts

                # Append to Google Sheet
                sheet = get_sheet_client()
                sheet.append_row([
                    enriched.get("input", ""),
                    enriched.get("app_name", ""),
                    enriched.get("purpose", ""),
                    enriched.get("author", ""),
                    enriched.get("github_link", ""),
                    enriched.get("paper_link", ""),
                    enriched.get("user", ""),
                    enriched.get("timestamp", "")
                ])
            else:
                print(f"Enrichment failed: {response.text}")

    return JSONResponse(content={"status": "ok"})
