import machine
import urequests

URL = 'https://raw.githubusercontent.com/<you>/<repo>/eink/dashboard.bin'


def fetch_frame():
    response = urequests.get(URL)
    try:
        return response.content   # 15,000 bytes for a 400x300 1-bit panel
    finally:
        response.close()


frame = fetch_frame()
# Hand `frame` to your display driver, then refresh the panel.
# Some panels expect inverted bits, so you may need to flip them.
machine.deepsleep(60 * 60 * 1000)   # sleep for an hour
