import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from Configs.config import ROOT_DIR

_key_path = os.path.join(ROOT_DIR, "assets", "service_account.json")
_scopes = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_file(_key_path, scopes=_scopes)
sheet = build("sheets", "v4", credentials=credentials).spreadsheets()

print("[LOG] Google Sheets ready")

service = {"sheet": sheet}
