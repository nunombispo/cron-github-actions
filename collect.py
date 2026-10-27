import os
from datetime import datetime, timezone

import psycopg
import requests

API = 'https://api.open-meteo.com/v1/forecast'
PARAMS = {
    'latitude': 52.09,
    'longitude': 5.12,
    'current': 'temperature_2m,wind_speed_10m',
    'timezone': 'UTC',
}

SCHEMA = (
    'CREATE TABLE IF NOT EXISTS readings ('
    'observed_at timestamptz PRIMARY KEY, '
    'temperature_c real NOT NULL, '
    'wind_kmh real NOT NULL)'
)

INSERT = (
    'INSERT INTO readings (observed_at, temperature_c, wind_kmh) '
    'VALUES (%s, %s, %s) '
    'ON CONFLICT (observed_at) DO NOTHING'
)


def fetch_reading():
    response = requests.get(API, params=PARAMS, timeout=15)
    response.raise_for_status()
    current = response.json()['current']
    observed_at = datetime.fromisoformat(current['time']).replace(tzinfo=timezone.utc)
    return observed_at, current['temperature_2m'], current['wind_speed_10m']


def store(reading):
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        conn.execute(SCHEMA)
        conn.execute(INSERT, reading)


if __name__ == '__main__':
    store(fetch_reading())
