#!/usr/bin/env python3
"""
Force-refresh: fetch the most recent LICH MO CT email from Gmail,
delete any existing OR Schedule events for that date, and create a
fresh grouped event. Ignores processed_emails.json — always re-runs
on the latest schedule regardless of prior processing.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from auth import get_gmail_service, get_calendar_service
from gmail_fetcher import (
    search_schedule_emails, get_email_subject,
    download_excel_attachment, extract_date_from_subject,
)
from excel_parser import parse_operations
from calendar_creator import create_grouped_event
from config import CALENDAR_ID, EMAIL_SUBJECT_KEYWORD


def delete_existing_events(service, operation_date):
    date_str = operation_date.strftime("%Y-%m-%d")
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=f"{date_str}T00:00:00+07:00",
        timeMax=f"{date_str}T23:59:59+07:00",
        singleEvents=True,
        maxResults=50,
    ).execute()

    deleted = 0
    for ev in result.get("items", []):
        summary = ev.get("summary", "")
        if "MO PT TIM" in summary or "OPERATION SCHEDULE" in summary or "OR Schedule" in summary:
            service.events().delete(calendarId=CALENDAR_ID, eventId=ev["id"]).execute()
            print(f"  Deleted: {summary}")
            deleted += 1

    if deleted == 0:
        print("  No existing events found for this date.")
    return deleted


def main():
    gmail = get_gmail_service()
    gcal = get_calendar_service()

    messages = search_schedule_emails(gmail, EMAIL_SUBJECT_KEYWORD)
    if not messages:
        print("No matching emails found.")
        sys.exit(0)

    # Most recent email is first
    msg = messages[0]
    msg_id = msg["id"]
    subject = get_email_subject(gmail, msg_id)
    print(f"Latest email: {subject}")

    operation_date = extract_date_from_subject(subject)
    if not operation_date:
        print(f"ERROR: Could not parse date from subject: {subject!r}")
        sys.exit(1)
    print(f"Operation date: {operation_date.strftime('%d/%m/%Y')}")

    filepath = download_excel_attachment(gmail, msg_id)
    if not filepath:
        print("ERROR: No Excel attachment found.")
        sys.exit(1)

    try:
        operations = parse_operations(filepath)
    finally:
        try:
            os.remove(filepath)
        except OSError:
            pass

    if not operations:
        print("No 'Pt tim' operations found in this email.")
        sys.exit(0)
    print(f"Found {len(operations)} Pt tim case(s).")

    print("Deleting existing events...")
    delete_existing_events(gcal, operation_date)

    print("Creating new grouped event...")
    event = create_grouped_event(gcal, operations, operation_date)
    print(f"Created: {event.get('summary')}")
    print(f"Link: {event.get('htmlLink')}")


if __name__ == "__main__":
    main()
