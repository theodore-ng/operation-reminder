# Commands

## Setup (first time)

```bash
pip install -r requirements.txt
python setup_oauth.py   # OAuth2 consent flow — opens browser
```

**Required files in project root before running:**
- `credentials.json` — OAuth2 client credentials from Google Cloud Console
- `.env` — contains `GEMINI_API_KEY=<your key>` (get a free key at aistudio.google.com)

## Daily run

```bash
python3 main.py
```

Processes only new (unprocessed) emails. Safe to run repeatedly — skips already-handled email IDs.

## Force-refresh upcoming schedule

```bash
python3 refresh_today.py
```

Fetches the most recent `LỊCH MỔ CT` email from Gmail regardless of processing history, deletes any existing OR Schedule events for that operation date, and creates a fresh grouped event. Use this after a corrected schedule email arrives.

## Cron (automated daily)

```cron
0 7 * * * cd /path/to/operation_reminder && python3 main.py >> operation_reminder.log 2>&1
```

## Version control

Tagged releases are on GitHub: https://github.com/theodore-ng/operation-reminder/releases

```bash
# Roll back to a specific version
git checkout v1.0.0

# Return to latest
git checkout main
```
