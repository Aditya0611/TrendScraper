import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config

class GoogleSheetsHandler:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.creds = None
        if not os.path.exists(Config.GOOGLE_SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Google Service Account file not found at: {Config.GOOGLE_SERVICE_ACCOUNT_FILE}. "
                                  "Please place your 'credentials.json' in the project folder.")
        
        self.creds = service_account.Credentials.from_service_account_file(
            Config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = self._extract_id(Config.GOOGLE_SHEET_ID)

    def _extract_id(self, sheet_input):
        """Extracts the Spreadsheet ID from a URL if provided, otherwise returns the input."""
        if "spreadsheets/d/" in sheet_input:
            # Handle URL format: https://docs.google.com/spreadsheets/d/ID/edit...
            parts = sheet_input.split("spreadsheets/d/")
            if len(parts) > 1:
                return parts[1].split("/")[0]
        return sheet_input

    def get_unprocessed_rows(self):
        """Fetches rows where Posting Status is not 'Posted'."""
        try:
            print(f"DEBUG: Fetching range A2:K from Spreadsheet ID: {self.spreadsheet_id}")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="A2:K").execute()
            values = result.get('values', [])
            
            print(f"DEBUG: Found {len(values)} total data rows in sheet.")
            
            unprocessed = []
            for i, row in enumerate(values):
                # Ensure row has enough columns
                while len(row) < 11:
                    row.append("")
                
                date = row[0].strip()
                topic = row[1].strip()
                tone = row[2].strip()
                platform = row[3].strip()
                status = row[8].strip().lower() # Case-insensitive check
                
                # Skip empty rows (no topic or no platform)
                if not topic or not platform:
                    continue
                
                if status != "posted":
                    unprocessed.append({
                        "row_index": i + 2, # 1-based index, plus header (row 1)
                        "data": {
                            "topic": topic,
                            "tone": tone,
                            "date": date,
                            "platform": platform,
                            "audience": row[4].strip(),
                            "keywords": row[5].strip(),
                            "cta": row[6].strip()
                        }
                    })
            
            print(f"DEBUG: Identified {len(unprocessed)} unprocessed rows ready for generation.")
            return unprocessed
        except Exception as e:
            print(f"Error reading sheets: {e}")
            return []

    def update_row_status(self, row_index, content, status, timestamp, error=""):
        """Updates the sheet with generation results and status."""
        range_name = f"H{row_index}:K{row_index}"
        values = [[content, status, timestamp, error]]
        body = {'values': values}
        
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=range_name,
                valueInputOption="RAW", body=body).execute()
        except Exception as e:
            print(f"Error updating sheet: {e}")
