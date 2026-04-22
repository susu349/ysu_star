"fc1260c8b9b976d5add3a37b4b0b821c"
import requests
import os
import math

TK = "fc1260c8b9b976d5add3a37b4b0b821c"
ZOOM = 16
LAT1, LON1 = 39.935, 119.465
LAT2, LON2 = 39.885, 119.585
SAVE_DIR = "haigang_tiles"
os.makedirs(SAVE_DIR, exist_ok=True)

def ll2xy(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lat_rad = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n)
    return x, y

x_min, y_max = ll2xy(LAT2, LON1, ZOOM)
x_max, y_min = ll2xy(LAT1, LON2, ZOOM)

for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        url = f"https://t0.tianditu.gov.cn/DataServer?T=img_w&X={x}&Y={y}&L={ZOOM}&tk={TK}"
        try:
            r = requests.get(url, timeout=10)
            with open(f"{SAVE_DIR}/{ZOOM}_{x}_{y}.png", "wb") as f:
                f.write(r.content)
            print(f"OK {ZOOM}_{x}_{y}.png")
        except Exception as e:
            print(f"FAIL {ZOOM}_{x}_{y}", e)
