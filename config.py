import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env if present
_env_file = os.path.join(SCRIPT_DIR, ".env")
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

DEPARTMENT_NAME = "Pt tim"
EMAIL_SUBJECT_KEYWORD = "LỊCH MỔ CT"
SEARCH_DAYS_BACK = 2  # Search emails from last 2 days to account for late delivery

CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
PROCESSED_FILE = os.path.join(SCRIPT_DIR, "processed_emails.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "operation_reminder.log")
DOWNLOAD_DIR = "/tmp"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

TIMEZONE = "Asia/Ho_Chi_Minh"
CALENDAR_ID = "primary"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

# Column indices in the Excel sheet (0-based)
COL_THU = 0       # Day of week
COL_STT = 1       # Sequential number
COL_PMO = 2       # Operating room
COL_TTCA = 3      # Order within room
COL_DK = 4        # Additional info
COL_KHOA = 5      # Department
COL_TEN = 6       # Patient name
COL_TUOI = 7      # Age
COL_CHAN_DOAN = 8  # Diagnosis
COL_PHAU_THUAT = 9 # Surgery method
COL_BAC_SI = 10   # Surgeon
COL_GHI_CHU = 11  # Notes
