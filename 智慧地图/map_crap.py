import tkinter as tk
from PIL import Image, ImageTk

class MapCropper:
    def __init__(self, root, img_path):
        self.root = root
        self.root.title("地图裁剪：滚轮缩放 左键平移 右键框选 C保存")

        self.original = Image.open(img_path)
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.pan_x = 0
        self.pan_y = 0

        self.box = None
        self.box_start = (0, 0)
        self.rect_coords = (0, 0, 0, 0)

        self.canvas = tk.Canvas(root, bg="#222")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)

        self.canvas.bind("<Button-3>", self.on_box_start)
        self.canvas.bind("<B3-Motion>", self.on_box_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_box_release)

        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.root.bind("c", self.do_crop)

        self.redraw()

    def to_img(self, x, y):
        return (int((x - self.offset_x) / self.scale), int((y - self.offset_y) / self.scale))

    def redraw(self):
        w, h = self.original.size
        nw = int(w * self.scale)
        nh = int(h * self.scale)
        self.tk_img = ImageTk.PhotoImage(self.original.resize((nw, nh), Image.Resampling.LANCZOS))
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.tk_img)
        if self.box:
            self.canvas.coords(self.box, self.rect_coords)

    def on_pan_start(self, e):
        self.pan_x, self.pan_y = e.x, e.y

    def on_pan_move(self, e):
        dx = e.x - self.pan_x
        dy = e.y - self.pan_y
        self.offset_x += dx
        self.offset_y += dy
        self.pan_x, self.pan_y = e.x, e.y
        self.redraw()

    def on_box_start(self, e):
        self.box_start = (e.x, e.y)
        if self.box:
            self.canvas.delete(self.box)
            self.box = None

    def on_box_drag(self, e):
        x1, y1 = self.box_start
        x2, y2 = e.x, e.y
        self.rect_coords = (x1, y1, x2, y2)
        if self.box:
            self.canvas.coords(self.box, self.rect_coords)
        else:
            self.box = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

    def on_box_release(self, e):
        pass

    def do_crop(self, event):
        if not self.box:
            print("请先框选区域")
            return

        x1, y1, x2, y2 = self.rect_coords
        ix1, iy1 = self.to_img(min(x1, x2), min(y1, y2))
        ix2, iy2 = self.to_img(max(x1, x2), max(y1, y2))

        ix1 = max(0, ix1)
        iy1 = max(0, iy1)
        ix2 = min(self.original.width, ix2)
        iy2 = min(self.original.height, iy2)

        out = self.original.crop((ix1, iy1, ix2, iy2))
        out.save("燕山大学_crop_result.png")
        print("保存成功：燕山大学_crop_result.png")
        self.root.quit()

    def on_wheel(self, e):
        s = 1.2 if e.delta > 0 else 0.8
        self.scale *= s
        self.scale = max(0.1, min(5.0, self.scale))
        self.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    MapCropper(root, "haigang.png")
    root.mainloop()
