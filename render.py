import os
from datetime import datetime, timezone

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import psycopg
from PIL import Image

WIDTH, HEIGHT = 400, 300

QUERY = (
    'SELECT observed_at, temperature_c FROM readings '
    'WHERE observed_at > now() - make_interval(hours => 24) '
    'ORDER BY observed_at'
)


def load_readings():
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        return conn.execute(QUERY).fetchall()


def render(rows):
    times = [row[0] for row in rows]
    temps = [row[1] for row in rows]

    fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100)
    ax = fig.add_axes([0.12, 0.18, 0.84, 0.68])
    ax.plot(times, temps, color='black', linewidth=2)
    ax.set_title(f'Utrecht, last 24h  |  now {temps[-1]:.1f} °C', fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, linewidth=0.3)
    fig.text(0.12, 0.03, f'updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC', fontsize=8)

    os.makedirs('out', exist_ok=True)
    fig.savefig('out/raw.png', facecolor='white')
    plt.close(fig)

    image = Image.open('out/raw.png').convert('1')
    image.save('out/dashboard.png')
    with open('out/dashboard.bin', 'wb') as f:
        f.write(image.tobytes())


if __name__ == '__main__':
    rows = load_readings()
    if not rows:
        raise SystemExit('No readings yet')
    render(rows)
