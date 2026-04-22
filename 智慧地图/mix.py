from PIL import Image
import os

ZOOM = 16
tile_dir = "haigang_tiles"
out = "haigang.png"

tiles = {}
xs = []
ys = []

for f in os.listdir(tile_dir):
    if f.endswith(".png"):
        z, x, y = f[:-4].split("_")
        x = int(x)
        y = int(y)
        xs.append(x)
        ys.append(y)
        tiles[(x, y)] = os.path.join(tile_dir, f)

x_min = min(xs)
x_max = max(xs)
y_min = min(ys)
y_max = max(ys)

w = (x_max - x_min + 1) * 256
h = (y_max - y_min + 1) * 256
img = Image.new("RGB", (w, h))

for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        tile = Image.open(tiles[(x, y)])
        px = (x - x_min) * 256
        py = (y - y_min) * 256
        img.paste(tile, (px, py))

img.save(out)
print("拼接完成：haigang.png")
from PIL import Image
import os

ZOOM = 16
tile_dir = "haigang_tiles"
out = "haigang.png"

tiles = {}
xs = []
ys = []

for f in os.listdir(tile_dir):
    if f.endswith(".png"):
        z, x, y = f[:-4].split("_")
        x = int(x)
        y = int(y)
        xs.append(x)
        ys.append(y)
        tiles[(x, y)] = os.path.join(tile_dir, f)

x_min = min(xs)
x_max = max(xs)
y_min = min(ys)
y_max = max(ys)

w = (x_max - x_min + 1) * 256
h = (y_max - y_min + 1) * 256
img = Image.new("RGB", (w, h))

for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        tile = Image.open(tiles[(x, y)])
        px = (x - x_min) * 256
        py = (y - y_min) * 256
        img.paste(tile, (px, py))

img.save(out)
print("拼接完成：haigang.png")
