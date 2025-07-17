import os
import datetime
import gspread
from google.oauth2.service_account import Credentials

def log_to_sheets(data):
    creds_json_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    try:
        creds = Credentials.from_service_account_file(
            creds_json_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).sheet1

        sheet.append_row([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["title"],
            data["description"],
            data["link"]
        ])
    except Exception as e:
        print(f"Error logging to Sheets: {e}")
