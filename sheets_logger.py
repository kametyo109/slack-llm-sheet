import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "Sheet1"

credentials = Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

def log_to_sheets(data: dict):
    row = [
        data.get("app_name", ""),
        data.get("purpose", ""),
        data.get("author", ""),
        data.get("github_link", ""),
        data.get("paper_link", "")
    ]
    sheet.append_row(row)
