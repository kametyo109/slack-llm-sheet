import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1

def log_to_sheets(data):
    sheet.append_row([
        data.get("timestamp", ""),
        data.get("name", ""),
        data.get("description", ""),
        data.get("author", ""),
        data.get("github", ""),
        data.get("paper", "")
    ])
