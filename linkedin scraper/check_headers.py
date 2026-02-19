import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config

def check_headers():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(
        Config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    # Extract ID logic
    sheet_input = Config.GOOGLE_SHEET_ID
    if "spreadsheets/d/" in sheet_input:
        parts = sheet_input.split("spreadsheets/d/")
        sheet_id = parts[1].split("/")[0]
    else:
        sheet_id = sheet_input

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A1:K1").execute()
    headers = result.get('values', [])
    print(f"HEADERS: {headers}")

if __name__ == "__main__":
    check_headers()
