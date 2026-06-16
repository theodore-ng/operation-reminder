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

## Re-authenticating after token expiry

If the GitHub Actions run fails with:
```
google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.', ...)
```
the `TOKEN_JSON` secret is dead. `auth.py` won't fall back to a fresh login on its own while a (dead) `refresh_token` is present in `token.json` — it tries to refresh and raises instead.

```bash
mv token.json token.json.expired.bak   # forces auth.py past the refresh branch into a fresh login
python3 setup_oauth.py                 # opens a browser, log in + grant access
gh secret set TOKEN_JSON < token.json  # push the new token to GitHub Actions
gh workflow run daily-reminder.yml     # optional: verify it goes green
```

Should be rare now that the OAuth consent screen's publishing status is "In production" (changed 2026-06-16) — tokens only die after ~6 months of inactivity or explicit revocation, not the 7-day expiry that "Testing" status enforces.

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
