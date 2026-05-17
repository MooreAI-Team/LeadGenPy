import json
import os
from Configs.google_api_config import service
from Configs import config
from dotenv import load_dotenv
load_dotenv()


class Store:
    __SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    sheet = service["sheet"]

    def __init__(self):
        self.generate_sheet_headers()

    # write headers only if the sheet is empty
    def generate_sheet_headers(self):
        result = self.sheet.values().get(
            spreadsheetId=self.__SPREADSHEET_ID,
            range="Sheet1!A1:A1"
        ).execute()
        if result.get('values'):
            return  # headers already there
        self.sheet.values().update(
            spreadsheetId=self.__SPREADSHEET_ID,
            range="Sheet1!A1:T1",
            valueInputOption="USER_ENTERED",
            body={"values": [config.headers]}
        ).execute()

    # this function will append the extracted data to a JSON file. it handles nonexistent or empty files as well.
    def append_to_json(self, data):
        json_path = os.path.join(config.ROOT_DIR, "assets/data.json")
        existing = []
        if os.path.exists(json_path):
            with open(json_path) as f:
                content = f.read()
            if content.strip():
                existing = json.loads(content)
        existing.append(data)
        with open(json_path, 'w') as f:
            json.dump(existing, f, indent=4)

    # check if a business link already exists in the JSON, it prevents duplicate runs
    def is_duplicate(self, maps_link):
        json_path = os.path.join(config.ROOT_DIR, "assets/data.json")
        if not os.path.exists(json_path):
            return False
        with open(json_path) as f:
            content = f.read()
        if not content.strip():
            return False
        data = json.loads(content)
        return any(entry.get("GoogleMapsLink") == maps_link for entry in data)

    # insert a single row into Google Sheets
    def insert_one_row(self, values):
        self.sheet.values().append(
            spreadsheetId=self.__SPREADSHEET_ID,
            range="Sheet1!A2:T2",
            valueInputOption="USER_ENTERED",
            body={'values': values}
        ).execute()
