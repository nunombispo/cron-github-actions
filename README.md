# cron-github-actions

Companion code for [Stop Paying for Cron: Running Scheduled Jobs on GitHub Actions](https://developer-service.blog).

Two scheduled GitHub Actions workflows: one collects hourly weather readings into Postgres, the other renders a 1-bit e-ink dashboard and publishes it to an `eink` branch for an ESP32 to download.

If this script was useful to you, consider donating to support the Developer Service Blog: https://buy.stripe.com/bIYdTrggi5lZamkdQW

## What’s in here

- **`collect.py`**: fetches current weather from Open-Meteo and inserts a row into Postgres.
- **`render.py`**: queries the last 24 hours and writes `out/dashboard.png` plus `out/dashboard.bin` (400×300 1-bit).
- **`.github/workflows/collect.yml`**: hourly collector (`:07` UTC) plus manual `workflow_dispatch`.
- **`.github/workflows/dashboard.yml`**: hourly renderer (`:12` UTC) that force-pushes the frame to the `eink` branch.
- **`device/main.py`**: MicroPython sketch that downloads `dashboard.bin` and deep-sleeps for an hour.

## Requirements

- Python 3.12+
- A Postgres database (Neon, Supabase, or similar) and its connection string

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set the database URL and run the collector locally:

```bash
export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'
python collect.py
python render.py
```

## GitHub Actions secrets

Under **Settings → Secrets and variables → Actions**, add:

- `DATABASE_URL` — Postgres connection string

Optional failure notification (add as a final step with `if: failure()`):

- `NTFY_TOPIC` — ntfy.sh topic name

After the first successful dashboard run, the frame is at:

```
https://raw.githubusercontent.com/<you>/<repo>/eink/dashboard.bin
```

Update `URL` in `device/main.py` to match your repo, then wire `frame` into your display driver.
