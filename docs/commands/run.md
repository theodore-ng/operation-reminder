# Commands

## Setup (first time)

```bash
pip install -r requirements.txt
python setup_oauth.py   # OAuth2 consent flow — opens browser
```

Place `credentials.json` from Google Cloud Console in the project root before running.

## Daily run

```bash
python main.py
```

Processes only new (unprocessed) emails. Safe to run repeatedly — skips already-handled email IDs.

## Force-refresh upcoming schedule

```bash
python refresh_today.py
```

Fetches the most recent `LỊCH MỔ CT` email from Gmail regardless of processing history, deletes any existing OR Schedule / MO PT TIM events for that operation date, and creates a fresh grouped event. Use this after a corrected schedule email arrives.

## Cron (automated daily)

```cron
0 7 * * * cd /path/to/operation_reminder && python main.py >> operation_reminder.log 2>&1
```
