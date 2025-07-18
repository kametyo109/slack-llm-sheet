import os
import datetime
import gspread
from google.oauth2.service_account import Credentials

def log_to_sheets(data):
    creds_json_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not spreadsheet_id:
        print("[Sheets] ERROR: SPREADSHEET_ID environment variable not set.")
        return

    if not os.path.exists(creds_json_path):
        print(f"[Sheets] ERROR: Credentials file not found at {creds_json_path}")
        return

    try:
        print("[Sheets] Authenticating...")
        creds = Credentials.from_service_account_file(
            creds_json_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        client = gspread.authorize(creds)
        print("[Sheets] Connected to Google Sheets API.")

        sheet = client.open_by_key(spreadsheet_id).sheet1
        print(f"[Sheets] Opened spreadsheet: {spreadsheet_id}")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, data["title"], data["description"], data["link"]]

        sheet.append_row(row)
        print(f"[Sheets] Successfully logged row: {row}")

    except Exception as e:
        print(f"[Sheets] ERROR while logging to Sheets: {e}")
