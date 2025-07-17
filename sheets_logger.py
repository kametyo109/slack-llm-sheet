import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "Sheet1"

import json

# Try to load credentials from environment variable first, then fallback to file
try:
    # Option 1: Load from environment variable (recommended for Render)
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        credentials_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    else:
        # Option 2: Load from file (local development)
        credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
except Exception as e:
    print(f"Error loading credentials: {e}")
    credentials = None
client = gspread.authorize(credentials) if credentials else None
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME) if client else None

def log_to_sheets(data: dict):
    """Log enriched Slack app data to Google Sheets starting from row 5"""
    if not sheet:
        print("Google Sheets not configured properly")
        return

    row = [
        data.get("date_added", ""),
        data.get("app_name", ""),
        data.get("app_description", ""),
        data.get("original_link", "")
    ]

    # Find the next empty row starting from row 5
    next_row = len(sheet.get_all_values()) + 1
    if next_row < 5:  # Ensure we start from row 5
        next_row = 5

    # Insert the row at the specific position
    sheet.insert_row(row, next_row)
    print(f"Logged to sheets at row {next_row}: {data.get('app_name', 'Unknown')}")

def setup_sheet_headers():
    """Set up column headers in row 4 of the Google Sheet (run once if needed)"""
    if not sheet:
        print("Google Sheets not configured properly")
        return

    try:
        headers = ["Data added", "Application Name", "Description", "Link"]

        # Check if headers already exist in row 4
        existing_headers = sheet.row_values(4)
        if not existing_headers or existing_headers != headers:
            # Clear row 4 and add headers
            sheet.delete_rows(4, 4)
            sheet.insert_row(headers, 4)
            print("Headers added to row 4")
        else:
            print("Headers already exist in row 4")
    except Exception as e:
        print(f"Error setting up headers: {e}")

if __name__ == "__main__":
    setup_sheet_headers()
