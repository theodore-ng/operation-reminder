#!/usr/bin/env python3
"""
Operation schedule reminder — fetches LICH MO CT emails from Gmail,
filters for the 'Pt tim' department in the attached Excel file,
and creates a single grouped Google Calendar event per operation day.
"""
import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from config import LOG_FILE, EMAIL_SUBJECT_KEYWORD

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def main():
    from auth import get_gmail_service, get_calendar_service
    from gmail_fetcher import (
        search_schedule_emails, load_processed_ids, save_processed_id,
        get_email_subject, download_excel_attachment, extract_date_from_subject,
    )
    from excel_parser import parse_operations
    from calendar_creator import grouped_event_exists, create_grouped_event

    log.info("=== Operation reminder check started ===")

    gmail = get_gmail_service()
    gcal = get_calendar_service()

    messages = search_schedule_emails(gmail, EMAIL_SUBJECT_KEYWORD)
    if not messages:
        log.info("No matching emails found today.")
        return

    log.info(f"Found {len(messages)} matching email(s)")
    processed_ids = load_processed_ids()
    total_created = 0

    for msg in messages:
        msg_id = msg["id"]
        if msg_id in processed_ids:
            log.info(f"Email {msg_id} already processed — skipping")
            continue

        subject = get_email_subject(gmail, msg_id)
        log.info(f"Processing: {subject}")

        operation_date = extract_date_from_subject(subject)
        if not operation_date:
            log.warning(f"Could not parse date from subject: {subject!r}")
            continue

        filepath = download_excel_attachment(gmail, msg_id)
        if not filepath:
            log.warning(f"No Excel attachment in email: {subject}")
            continue

        try:
            operations = parse_operations(filepath)
        finally:
            try:
                os.remove(filepath)
            except OSError:
                pass

        if not operations:
            log.info(f"No 'Pt tim' operations found in {subject}")
            save_processed_id(msg_id)
            continue

        date_display = operation_date.strftime("%d/%m/%Y")
        log.info(f"Found {len(operations)} Pt tim operation(s) for {date_display}")

        if grouped_event_exists(gcal, operation_date):
            log.info(f"Grouped operation event already exists for {date_display} — skipping")
        else:
            try:
                event = create_grouped_event(gcal, operations, operation_date)
                log.info(f"Created grouped event: {event.get('summary')}")
                total_created += 1
            except Exception as e:
                log.error(f"Failed to create grouped event for {date_display}: {e}")

        save_processed_id(msg_id)

    log.info(f"=== Done. {total_created} new calendar event(s) created ===")


if __name__ == "__main__":
    main()
