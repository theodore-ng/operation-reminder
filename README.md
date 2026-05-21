# Operation Reminder — Pt tim Department

Automatically checks Gmail at 5 PM daily for the weekly operation schedule email,
filters for **Pt tim** department cases, and creates Google Calendar reminders.

---

## One-time Google API Setup

You only need to do this once.

### Step 1 — Create a Google Cloud project

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g. "Operation Reminder")
3. In the left menu → **APIs & Services** → **Library**
4. Enable **Gmail API**
5. Enable **Google Calendar API**

### Step 2 — Create OAuth credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name it anything (e.g. "operation-reminder")
5. Click **Download JSON** → rename it to `credentials.json`
6. Move `credentials.json` into this folder:
   ```
   /home/dongtrieu/codes/operation_reminder/credentials.json
   ```

### Step 3 — OAuth consent screen (if prompted)

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** → fill in app name and your email
3. Add scopes: `gmail.readonly` and `calendar.events`
4. Add your Gmail address under **Test users**

### Step 4 — Authorize the app

Run this once — it will open a browser window for you to log in:

```bash
python3 /home/dongtrieu/codes/operation_reminder/setup_oauth.py
```

A `token.json` file will be saved. After this, the script runs silently every day.

---

## Manual test run

```bash
python3 /home/dongtrieu/codes/operation_reminder/main.py
```

---

## Schedule

The cron job runs automatically every day at **17:00 (5 PM)**:

```
0 17 * * * /bin/python3 /home/dongtrieu/codes/operation_reminder/main.py
```

To check or modify it: `crontab -e`

---

## Logs

- `operation_reminder.log` — full run log with timestamps
- `cron.log` — cron output
- `processed_emails.json` — tracks which email IDs have already been processed (prevents duplicates)

---

## What gets created in Google Calendar

One all-day event per patient in the **Pt tim** department, on the operation date, with:
- Patient name and surgery as the title
- Diagnosis, surgery method, surgeon names, operating room
- Pop-up reminders: **1 day before** and **1 hour before**
- Red color label

---

## Configuration (`config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `DEPARTMENT_NAME` | `Pt tim` | Department to filter for |
| `EMAIL_SUBJECT_KEYWORD` | `LỊCH MỔ CT` | Gmail search keyword |
| `SEARCH_DAYS_BACK` | `2` | How many days back to search for emails |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` | Timezone for calendar events |
