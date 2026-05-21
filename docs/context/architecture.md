# Architecture

## Pipeline

1. Search Gmail for emails with subject `LỊCH MỔ CT` that have an Excel attachment
2. Skip already-processed email IDs (tracked in `processed_emails.json`)
3. Parse the Excel — filter rows where `Khoa = "Pt tim"`
4. Send all cases to Gemini in one batch — Gemini groups by surgery category, chooses academic English names, and translates diagnosis + procedure
5. Create **one grouped timed Calendar event** (06:00–23:59) per operation day with all cases
6. Fire a single popup reminder at **6:00 AM on the operation day**

## File structure

```
operation_reminder/
├── main.py               # Entry point — full Gmail → Calendar pipeline
├── refresh_today.py      # Force-refresh from latest Gmail email, ignores processed cache
├── auth.py               # Google OAuth2 (Gmail + Calendar scopes)
├── config.py             # Column indices, keywords, file paths, calendar settings
├── gmail_fetcher.py      # Gmail search, Excel attachment download, date parsing
├── excel_parser.py       # openpyxl parser — filters rows by department name
├── calendar_creator.py   # Surgery classifier + grouped event builder
├── samples/              # Reference Excel files to understand the schedule format — never read by scripts
├── credentials.json      # OAuth2 client credentials (do NOT commit)
├── token.json            # OAuth2 token cache (do NOT commit)
└── processed_emails.json # Tracks already-processed Gmail message IDs
```

## Key design decisions

- One event per day (not per patient) to avoid notification spam
- Event is a timed block (06:00–23:59) not all-day, so a `minutes: 0` popup fires exactly at 6 AM — Google Calendar all-day events can't reliably target post-midnight times via the API
- Gemini groups cases and chooses its own academic category names; keyword-based fallback (`_CATEGORY_RULES`) is used when `GEMINI_API_KEY` is not set
- Room code `TIM` is mapped to "Heart Surgery OR" in the Gemini prompt; other room codes are passed as-is
- Separator between groups is `◆ ─ ◆` — short enough not to wrap on iPhone
- `refresh_today.py` always re-fetches from Gmail — use it to update a future schedule after a new email arrives
- `samples/` exists only so Claude can inspect the Excel structure when helping with code; no script reads from it
