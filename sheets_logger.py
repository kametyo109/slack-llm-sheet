import os
import datetime
import base64
import gspread
from google.oauth2.service_account import Credentials

def log_to_sheets(data):
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        print("[Sheets] ERROR: SPREADSHEET_ID environment variable not set.")
        return

    try:
        # Load credentials
        creds_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
        if creds_base64:
            creds_path = "/tmp/credentials.json"
            print("[Sheets] Using base64-encoded credentials from environment variable...")
            with open(creds_path, "wb") as f:
                f.write(base64.b64decode(creds_base64))
        else:
            creds_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
            print(f"[Sheets] Using local credentials file at: {creds_path}")
            if not os.path.exists(creds_path):
                print(f"[Sheets] ERROR: Credentials file not found at {creds_path}")
                return

        # Authenticate and connect to sheet
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print(f"[Sheets] Connected to spreadsheet: {spreadsheet_id}")

        # Find header row (assume "Date" is in column A)
        header_row_index = 1
        all_values = sheet.get_all_values()
        for i, row in enumerate(all_values):
            if row and row[0].strip().lower() == "date":
                header_row_index = i + 1
                break

        insert_index = header_row_index + 1

        # Compose row
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            data.get("title", "N/A"),
            data.get("description", "N/A"),
            data.get("link", "N/A")
        ]

        sheet.insert_row(row, index=insert_index)
        print(f"[Sheets] Inserted row below header (row {insert_index}): {row}")

    except Exception as e:
        print(f"[Sheets] ERROR while logging to Sheets: {e}")
