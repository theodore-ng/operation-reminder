import base64
import os
import re
import json
from datetime import datetime
from typing import Optional

from config import PROCESSED_FILE, DOWNLOAD_DIR, SEARCH_DAYS_BACK


def search_schedule_emails(service, keyword: str) -> list:
    query = f'subject:("{keyword}") newer_than:{SEARCH_DAYS_BACK}d has:attachment'
    result = service.users().messages().list(userId="me", q=query).execute()
    return result.get("messages", [])


def load_processed_ids() -> set:
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE) as f:
            return set(json.load(f))
    return set()


def save_processed_id(msg_id: str):
    ids = load_processed_ids()
    ids.add(msg_id)
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(ids), f)


def get_email_subject(service, msg_id: str) -> str:
    msg = service.users().messages().get(userId="me", id=msg_id, format="metadata",
                                         metadataHeaders=["Subject"]).execute()
    for h in msg["payload"]["headers"]:
        if h["name"] == "Subject":
            return h["value"]
    return ""


def download_excel_attachment(service, msg_id: str) -> Optional[str]:
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    parts = _flatten_parts(msg["payload"])

    for part in parts:
        filename = part.get("filename", "")
        mime = part.get("mimeType", "")
        is_excel = (
            filename.endswith(".xlsx")
            or filename.endswith(".xls")
            or "spreadsheet" in mime
            or "excel" in mime
        )
        if not is_excel:
            continue

        body = part.get("body", {})
        if "data" in body:
            data = body["data"]
        elif "attachmentId" in body:
            att = service.users().messages().attachments().get(
                userId="me", messageId=msg_id, id=body["attachmentId"]
            ).execute()
            data = att["data"]
        else:
            continue

        file_bytes = base64.urlsafe_b64decode(data)
        safe_name = re.sub(r'[^\w\-.]', '_', filename) or "schedule.xlsx"
        filepath = os.path.join(DOWNLOAD_DIR, safe_name)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        return filepath

    return None


def extract_date_from_subject(subject: str) -> Optional[datetime]:
    # Match DD.MM.YYYY anywhere in the subject
    match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', subject)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass
    return None


def _flatten_parts(payload: dict) -> list:
    parts = []
    if payload.get("filename"):
        parts.append(payload)
    for part in payload.get("parts", []):
        parts.extend(_flatten_parts(part))
    return parts
