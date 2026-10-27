import os
from datetime import datetime, timezone

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import psycopg
from PIL import Image, ImageOps

WIDTH, HEIGHT = 400, 300
# Render sharp at 2x, then nearest-neighbour downscale for cleaner 1-bit text/lines.
SCALE = 2

QUERY = (
    'SELECT observed_at, temperature_c FROM readings '
    'WHERE observed_at > now() - make_interval(hours => 24) '
    'ORDER BY observed_at'
)


def load_readings():
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        return conn.execute(QUERY).fetchall()


def _style_axes(ax):
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1.2)
    ax.tick_params(colors='black', width=1.0, length=4, labelsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune=None))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=timezone.utc))
    ax.grid(True, which='major', color='black', linewidth=0.7, linestyle=':')
    ax.set_axisbelow(True)


def render(rows):
    times = [row[0] for row in rows]
    temps = [row[1] for row in rows]
    current = temps[-1]
    t_min, t_max = min(temps), max(temps)

    fig = plt.figure(
        figsize=(WIDTH / 100, HEIGHT / 100),
        dpi=100 * SCALE,
        facecolor='white',
    )
    ax = fig.add_axes([0.14, 0.15, 0.80, 0.58])
    _style_axes(ax)

    ax.plot(
        times,
        temps,
        color='black',
        linewidth=2.4,
        solid_capstyle='round',
        solid_joinstyle='round',
        zorder=3,
    )
    ax.plot(
        times,
        temps,
        linestyle='None',
        marker='o',
        markersize=4.5,
        markerfacecolor='black',
        markeredgecolor='black',
        zorder=4,
    )

    # Keep a little headroom so the line does not kiss the frame.
    pad = max(0.3, (t_max - t_min) * 0.2) if t_max != t_min else 0.5
    ax.set_ylim(t_min - pad, t_max + pad)
    x0 = mdates.date2num(times[0])
    x1 = mdates.date2num(times[-1])
    x_pad = max((x1 - x0) * 0.05, 1 / 48)  # at least ~30 minutes
    ax.set_xlim(x0 - x_pad, x1 + x_pad)

    fig.text(
        0.14,
        0.90,
        'Utrecht',
        fontsize=11,
        fontweight='bold',
        color='black',
        va='top',
    )
    fig.text(
        0.94,
        0.90,
        f'{current:.1f}°C',
        fontsize=15,
        fontweight='bold',
        color='black',
        ha='right',
        va='top',
    )
    fig.text(
        0.14,
        0.81,
        f'last 24h   min {t_min:.1f}   max {t_max:.1f}',
        fontsize=8,
        color='black',
        va='top',
    )
    fig.text(
        0.14,
        0.03,
        f'updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC',
        fontsize=7,
        color='black',
    )

    os.makedirs('out', exist_ok=True)
    fig.savefig('out/raw.png', facecolor='white', dpi=100 * SCALE)
    plt.close(fig)

    # Grayscale → high-contrast threshold (no dither) → exact panel size.
    image = Image.open('out/raw.png').convert('L')
    image = ImageOps.autocontrast(image, cutoff=1)
    image = image.point(lambda p: 255 if p > 160 else 0, mode='1')
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
    image.save('out/dashboard.png')
    with open('out/dashboard.bin', 'wb') as f:
        f.write(image.tobytes())


if __name__ == '__main__':
    rows = load_readings()
    if not rows:
        raise SystemExit('No readings yet')
    render(rows)
