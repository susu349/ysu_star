import tkinter as tk
from PIL import Image, ImageTk

class MapCropper:
    def __init__(self, root, img_path):
        self.root = root
        self.root.title("地图裁剪 | 9点拖拽调整 | 左键平移 右键画框 C保存")
        self.root.state("zoomed")
        self.root.update()

        # ========== 基础配置，可自行修改 ==========
        self.default_scale = 1 / 1.5  # 打开默认缩小1.5倍
        self.handle_size = 8  # 控制点大小
        self.handle_color = "#ffffff"  # 控制点填充色
        self.handle_border = "#ff0000"  # 控制点边框色
        self.box_color = "#ff0000"  # 裁剪框颜色
        # ==========================================

        # 加载原图
        self.original_img = Image.open(img_path)
        self.ori_w, self.ori_h = self.original_img.size

        # 地图显示状态
        self.current_scale = self.default_scale
        self.offset_x = 0
        self.offset_y = 0

        # 平移状态
        self.is_panning = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # 裁剪框核心状态（基于原图绝对坐标，永久绑定地图）
        self.box_x1 = None  # 框左边界（原图坐标）
        self.box_y1 = None  # 框上边界（原图坐标）
        self.box_x2 = None  # 框右边界（原图坐标）
        self.box_y2 = None  # 框下边界（原图坐标）

        # 9个控制点配置：索引、位置、对应光标
        self.handles = [
            {"id": 0, "pos": "nw", "cursor": "sizing_nw"},  # 左上
            {"id": 1, "pos": "n",  "cursor": "sizing_n"},   # 上中
            {"id": 2, "pos": "ne", "cursor": "sizing_ne"},  # 右上
            {"id": 3, "pos": "w",  "cursor": "sizing_w"},   # 左中
            {"id": 4, "pos": "c",  "cursor": "fleur"},      # 中心（移动整个框）
            {"id": 5, "pos": "e",  "cursor": "sizing_e"},   # 右中
            {"id": 6, "pos": "sw", "cursor": "sizing_sw"},  # 左下
            {"id": 7, "pos": "s",  "cursor": "sizing_s"},   # 下中
            {"id": 8, "pos": "se", "cursor": "sizing_se"},  # 右下
        ]
        self.handle_items = []  # 存储控制点的canvas对象
        self.box_item = None    # 存储裁剪框的canvas对象

        # 拖拽状态
        self.dragging_handle = None  # 当前正在拖拽的控制点ID
        self.drag_start_ori_x = 0    # 拖拽开始时的原图X坐标
        self.drag_start_ori_y = 0    # 拖拽开始时的原图Y坐标
        self.drag_start_box = None   # 拖拽开始时的框坐标

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg="#121212")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 事件绑定（Debian13专属完美适配）
        # 左键事件：平移地图 + 拖拽控制点
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        # 右键事件：画新的裁剪框
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        # 滚轮事件：缩放地图
        self.canvas.bind("<Button-4>", self.zoom_in)
        self.canvas.bind("<Button-5>", self.zoom_out)
        # 鼠标移动事件：hover控制点变光标
        self.canvas.bind("<Motion>", self.on_mouse_move)
        # 裁剪快捷键
        self.root.bind("c", self.do_crop)
        self.root.bind("C", self.do_crop)

        # 初始化地图居中显示
        self.root.after(100, self.init_map)

    # ===================== 坐标转换核心（地图和屏幕坐标互转） =====================
    def screen_to_ori(self, screen_x, screen_y):
        """屏幕坐标 → 原图绝对像素坐标"""
        ori_x = (screen_x - self.offset_x) / self.current_scale
        ori_y = (screen_y - self.offset_y) / self.current_scale
        return int(ori_x), int(ori_y)

    def ori_to_screen(self, ori_x, ori_y):
        """原图绝对像素坐标 → 屏幕坐标"""
        screen_x = ori_x * self.current_scale + self.offset_x
        screen_y = ori_y * self.current_scale + self.offset_y
        return int(screen_x), int(screen_y)

    # ===================== 初始化与重绘 =====================
    def init_map(self):
        """初始化地图：默认缩小1.5倍，居中显示"""
        window_w = self.root.winfo_width()
        window_h = self.root.winfo_height()
        scaled_w = self.ori_w * self.current_scale
        scaled_h = self.ori_h * self.current_scale
        self.offset_x = (window_w - scaled_w) / 2
        self.offset_y = (window_h - scaled_h) / 2
        self.redraw_all()

    def redraw_all(self):
        """全量重绘：地图 + 裁剪框 + 9个控制点（平移/缩放时自动调用）"""
        # 1. 重绘地图图片
        scaled_w = int(self.ori_w * self.current_scale)
        scaled_h = int(self.ori_h * self.current_scale)
        display_img = self.original_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        self.tk_display_img = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_display_img)

        # 2. 如果有裁剪框，重绘框和控制点
        if self.box_x1 is not None:
            # 转换框的屏幕坐标
            x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
            x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
            # 绘制裁剪框
            self.box_item = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=self.box_color, width=2, dash=(6, 3)
            )
            # 计算9个控制点的屏幕位置
            cx = (x1 + x2) / 2  # 中心X
            cy = (y1 + y2) / 2  # 中心Y
            handle_positions = [
                (x1, y1),  # 0 左上
                (cx, y1),  # 1 上中
                (x2, y1),  # 2 右上
                (x1, cy),  # 3 左中
                (cx, cy),  # 4 中心
                (x2, cy),  # 5 右中
                (x1, y2),  # 6 左下
                (cx, y2),  # 7 下中
                (x2, y2),  # 8 右下
            ]
            # 绘制9个控制点
            self.handle_items = []
            half = self.handle_size / 2
            for (hx, hy) in handle_positions:
                handle = self.canvas.create_rectangle(
                    hx - half, hy - half, hx + half, hy + half,
                    fill=self.handle_color, outline=self.handle_border, width=1
                )
                self.handle_items.append(handle)

    # ===================== 鼠标hover事件：控制点变光标 =====================
    def on_mouse_move(self, e):
        """鼠标移动时，hover到控制点自动切换对应光标"""
        # 如果没有裁剪框，默认箭头光标
        if self.box_x1 is None:
            self.canvas.config(cursor="arrow")
            return

        # 检查鼠标是否在某个控制点上
        x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
        x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
        cx, cy = (x1+x2)/2, (y1+y2)/2
        half = self.handle_size / 2

        # 9个控制点的屏幕范围
        handle_areas = [
            (x1-half, y1-half, x1+half, y1+half),  # 0 左上
            (cx-half, y1-half, cx+half, y1+half),  # 1 上中
            (x2-half, y1-half, x2+half, y1+half),  # 2 右上
            (x1-half, cy-half, x1+half, cy+half),  # 3 左中
            (cx-half, cy-half, cx+half, cy+half),  # 4 中心
            (x2-half, cy-half, x2+half, cy+half),  # 5 右中
            (x1-half, y2-half, x1+half, y2+half),  # 6 左下
            (cx-half, y2-half, cx+half, y2+half),  # 7 下中
            (x2-half, y2-half, x2+half, y2+half),  # 8 右下
        ]

        # 检查鼠标在哪个控制点上
        for i, (hx1, hy1, hx2, hy2) in enumerate(handle_areas):
            if hx1 <= e.x <= hx2 and hy1 <= e.y <= hy2:
                self.canvas.config(cursor=self.handles[i]["cursor"])
                return

        # 不在控制点上，默认箭头光标
        self.canvas.config(cursor="arrow")

    # ===================== 左键事件：平移地图 + 拖拽控制点 =====================
    def on_left_press(self, e):
        """左键按下：判断是拖拽控制点，还是平移地图"""
        # 如果有裁剪框，先检查是否点中了控制点
        if self.box_x1 is not None:
            x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
            x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
            cx, cy = (x1+x2)/2, (y1+y2)/2
            half = self.handle_size / 2

            handle_areas = [
                (x1-half, y1-half, x1+half, y1+half),
                (cx-half, y1-half, cx+half, y1+half),
                (x2-half, y1-half, x2+half, y1+half),
                (x1-half, cy-half, x1+half, cy+half),
                (cx-half, cy-half, cx+half, cy+half),
                (x2-half, cy-half, x2+half, cy+half),
                (x1-half, y2-half, x1+half, y2+half),
                (cx-half, y2-half, cx+half, y2+half),
                (x2-half, y2-half, x2+half, y2+half),
            ]

            # 检查是否点中控制点
            for i, (hx1, hy1, hx2, hy2) in enumerate(handle_areas):
                if hx1 <= e.x <= hx2 and hy1 <= e.y <= hy2:
                    self.dragging_handle = i
                    self.drag_start_ori_x, self.drag_start_ori_y = self.screen_to_ori(e.x, e.y)
                    self.drag_start_box = (self.box_x1, self.box_y1, self.box_x2, self.box_y2)
                    return

        # 没点中控制点，进入平移模式
        self.is_panning = True
        self.last_mouse_x = e.x
        self.last_mouse_y = e.y

    def on_left_drag(self, e):
        """左键拖动：拖拽控制点 或 平移地图"""
        # 正在拖拽控制点
        if self.dragging_handle is not None:
            current_ori_x, current_ori_y = self.screen_to_ori(e.x, e.y)
            dx = current_ori_x - self.drag_start_ori_x
            dy = current_ori_y - self.drag_start_ori_y
            x1, y1, x2, y2 = self.drag_start_box

            # 根据拖拽的控制点ID，更新框的坐标
            handle_id = self.dragging_handle
            if handle_id == 0:  # 左上
                new_x1, new_y1 = x1 + dx, y1 + dy
                self.box_x1 = min(new_x1, x2 - 10)
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 1:  # 上中
                new_y1 = y1 + dy
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 2:  # 右上
                new_x2, new_y1 = x2 + dx, y1 + dy
                self.box_x2 = max(new_x2, x1 + 10)
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 3:  # 左中
                new_x1 = x1 + dx
                self.box_x1 = min(new_x1, x2 - 10)
            elif handle_id == 4:  # 中心：移动整个框
                self.box_x1 = x1 + dx
                self.box_y1 = y1 + dy
                self.box_x2 = x2 + dx
                self.box_y2 = y2 + dy
            elif handle_id == 5:  # 右中
                new_x2 = x2 + dx
                self.box_x2 = max(new_x2, x1 + 10)
            elif handle_id == 6:  # 左下
                new_x1, new_y2 = x1 + dx, y2 + dy
                self.box_x1 = min(new_x1, x2 - 10)
                self.box_y2 = max(new_y2, y1 + 10)
            elif handle_id == 7:  # 下中
                new_y2 = y2 + dy
                self.box_y2 = max(new_y2, y1 + 10)
            elif handle_id == 8:  # 右下
                new_x2, new_y2 = x2 + dx, y2 + dy
                self.box_x2 = max(new_x2, x1 + 10)
                self.box_y2 = max(new_y2, y1 + 10)

            # 限制框不能超出原图边界
            self.box_x1 = max(0, self.box_x1)
            self.box_y1 = max(0, self.box_y1)
            self.box_x2 = min(self.ori_w, self.box_x2)
            self.box_y2 = min(self.ori_h, self.box_y2)

            # 重绘
            self.redraw_all()
            return

        # 正在平移地图
        if self.is_panning:
            dx = e.x - self.last_mouse_x
            dy = e.y - self.last_mouse_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_mouse_x = e.x
            self.last_mouse_y = e.y
            self.redraw_all()

    def on_left_release(self, e):
        """左键松开：结束拖拽/平移"""
        self.dragging_handle = None
        self.is_panning = False

    # ===================== 右键事件：画新的裁剪框 =====================
    def on_right_press(self, e):
        """右键按下：开始画新框"""
        start_ori_x, start_ori_y = self.screen_to_ori(e.x, e.y)
        self.box_x1 = start_ori_x
        self.box_y1 = start_ori_y
        self.box_x2 = start_ori_x
        self.box_y2 = start_ori_y

    def on_right_drag(self, e):
        """右键拖动：实时更新框的大小"""
        end_ori_x, end_ori_y = self.screen_to_ori(e.x, e.y)
        self.box_x2 = end_ori_x
        self.box_y2 = end_ori_y
        self.redraw_all()

    def on_right_release(self, e):
        """右键松开：完成画框，自动生成9个控制点"""
        # 修正框的坐标（确保x1<x2，y1<y2）
        self.box_x1, self.box_x2 = sorted([self.box_x1, self.box_x2])
        self.box_y1, self.box_y2 = sorted([self.box_y1, self.box_y2])
        # 限制框最小尺寸
        if self.box_x2 - self.box_x1 < 10:
            self.box_x2 = self.box_x1 + 10
        if self.box_y2 - self.box_y1 < 10:
            self.box_y2 = self.box_y1 + 10
        # 重绘，显示框和控制点
        self.redraw_all()

    # ===================== 滚轮缩放功能 =====================
    def zoom_at_mouse(self, mouse_x, mouse_y, factor):
        """以鼠标为中心缩放，框和控制点跟着地图一起缩放"""
        ori_x, ori_y = self.screen_to_ori(mouse_x, mouse_y)
        self.current_scale *= factor
        self.current_scale = max(0.1, min(5.0, self.current_scale))
        self.offset_x = mouse_x - (ori_x * self.current_scale)
        self.offset_y = mouse_y - (ori_y * self.current_scale)
        self.redraw_all()

    def zoom_in(self, e):
        self.zoom_at_mouse(e.x, e.y, 1.2)

    def zoom_out(self, e):
        self.zoom_at_mouse(e.x, e.y, 0.8)

    # ===================== 裁剪保存功能 =====================
    def do_crop(self, event):
        """按C键裁剪，保存原图高清分辨率"""
        if self.box_x1 is None:
            print("⚠️  请先右键画框，再按C键裁剪")
            return
        # 修正坐标
        x1 = max(0, int(self.box_x1))
        y1 = max(0, int(self.box_y1))
        x2 = min(self.ori_w, int(self.box_x2))
        y2 = min(self.ori_h, int(self.box_y2))
        # 裁剪并保存
        cropped_img = self.original_img.crop((x1, y1, x2, y2))
        cropped_img.save("燕山大学_裁剪结果.png")
        print(f"✅ 裁剪完成！")
        print(f"📐 裁剪尺寸：{x2-x1} × {y2-y1} 像素")
        print(f"💾 已保存为：燕山大学_裁剪结果.png")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    MapCropper(root, "haigang.png")
    root.mainloop()
import tkinter as tk
from PIL import Image, ImageTk

class MapCropper:
    def __init__(self, root, img_path):
        self.root = root
        self.root.title("地图裁剪 | 9点拖拽调整 | 左键平移 右键画框 C保存")
        self.root.state("zoomed")
        self.root.update()

        # ========== 基础配置，可自行修改 ==========
        self.default_scale = 1 / 1.5  # 打开默认缩小1.5倍
        self.handle_size = 8  # 控制点大小
        self.handle_color = "#ffffff"  # 控制点填充色
        self.handle_border = "#ff0000"  # 控制点边框色
        self.box_color = "#ff0000"  # 裁剪框颜色
        # ==========================================

        # 加载原图
        self.original_img = Image.open(img_path)
        self.ori_w, self.ori_h = self.original_img.size

        # 地图显示状态
        self.current_scale = self.default_scale
        self.offset_x = 0
        self.offset_y = 0

        # 平移状态
        self.is_panning = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # 裁剪框核心状态（基于原图绝对坐标，永久绑定地图）
        self.box_x1 = None  # 框左边界（原图坐标）
        self.box_y1 = None  # 框上边界（原图坐标）
        self.box_x2 = None  # 框右边界（原图坐标）
        self.box_y2 = None  # 框下边界（原图坐标）

        # 9个控制点配置：索引、位置、对应光标
        self.handles = [
            {"id": 0, "pos": "nw", "cursor": "sizing_nw"},  # 左上
            {"id": 1, "pos": "n",  "cursor": "sizing_n"},   # 上中
            {"id": 2, "pos": "ne", "cursor": "sizing_ne"},  # 右上
            {"id": 3, "pos": "w",  "cursor": "sizing_w"},   # 左中
            {"id": 4, "pos": "c",  "cursor": "fleur"},      # 中心（移动整个框）
            {"id": 5, "pos": "e",  "cursor": "sizing_e"},   # 右中
            {"id": 6, "pos": "sw", "cursor": "sizing_sw"},  # 左下
            {"id": 7, "pos": "s",  "cursor": "sizing_s"},   # 下中
            {"id": 8, "pos": "se", "cursor": "sizing_se"},  # 右下
        ]
        self.handle_items = []  # 存储控制点的canvas对象
        self.box_item = None    # 存储裁剪框的canvas对象

        # 拖拽状态
        self.dragging_handle = None  # 当前正在拖拽的控制点ID
        self.drag_start_ori_x = 0    # 拖拽开始时的原图X坐标
        self.drag_start_ori_y = 0    # 拖拽开始时的原图Y坐标
        self.drag_start_box = None   # 拖拽开始时的框坐标

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg="#121212")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 事件绑定（Debian13专属完美适配）
        # 左键事件：平移地图 + 拖拽控制点
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        # 右键事件：画新的裁剪框
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        # 滚轮事件：缩放地图
        self.canvas.bind("<Button-4>", self.zoom_in)
        self.canvas.bind("<Button-5>", self.zoom_out)
        # 鼠标移动事件：hover控制点变光标
        self.canvas.bind("<Motion>", self.on_mouse_move)
        # 裁剪快捷键
        self.root.bind("c", self.do_crop)
        self.root.bind("C", self.do_crop)

        # 初始化地图居中显示
        self.root.after(100, self.init_map)

    # ===================== 坐标转换核心（地图和屏幕坐标互转） =====================
    def screen_to_ori(self, screen_x, screen_y):
        """屏幕坐标 → 原图绝对像素坐标"""
        ori_x = (screen_x - self.offset_x) / self.current_scale
        ori_y = (screen_y - self.offset_y) / self.current_scale
        return int(ori_x), int(ori_y)

    def ori_to_screen(self, ori_x, ori_y):
        """原图绝对像素坐标 → 屏幕坐标"""
        screen_x = ori_x * self.current_scale + self.offset_x
        screen_y = ori_y * self.current_scale + self.offset_y
        return int(screen_x), int(screen_y)

    # ===================== 初始化与重绘 =====================
    def init_map(self):
        """初始化地图：默认缩小1.5倍，居中显示"""
        window_w = self.root.winfo_width()
        window_h = self.root.winfo_height()
        scaled_w = self.ori_w * self.current_scale
        scaled_h = self.ori_h * self.current_scale
        self.offset_x = (window_w - scaled_w) / 2
        self.offset_y = (window_h - scaled_h) / 2
        self.redraw_all()

    def redraw_all(self):
        """全量重绘：地图 + 裁剪框 + 9个控制点（平移/缩放时自动调用）"""
        # 1. 重绘地图图片
        scaled_w = int(self.ori_w * self.current_scale)
        scaled_h = int(self.ori_h * self.current_scale)
        display_img = self.original_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        self.tk_display_img = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_display_img)

        # 2. 如果有裁剪框，重绘框和控制点
        if self.box_x1 is not None:
            # 转换框的屏幕坐标
            x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
            x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
            # 绘制裁剪框
            self.box_item = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=self.box_color, width=2, dash=(6, 3)
            )
            # 计算9个控制点的屏幕位置
            cx = (x1 + x2) / 2  # 中心X
            cy = (y1 + y2) / 2  # 中心Y
            handle_positions = [
                (x1, y1),  # 0 左上
                (cx, y1),  # 1 上中
                (x2, y1),  # 2 右上
                (x1, cy),  # 3 左中
                (cx, cy),  # 4 中心
                (x2, cy),  # 5 右中
                (x1, y2),  # 6 左下
                (cx, y2),  # 7 下中
                (x2, y2),  # 8 右下
            ]
            # 绘制9个控制点
            self.handle_items = []
            half = self.handle_size / 2
            for (hx, hy) in handle_positions:
                handle = self.canvas.create_rectangle(
                    hx - half, hy - half, hx + half, hy + half,
                    fill=self.handle_color, outline=self.handle_border, width=1
                )
                self.handle_items.append(handle)

    # ===================== 鼠标hover事件：控制点变光标 =====================
    def on_mouse_move(self, e):
        """鼠标移动时，hover到控制点自动切换对应光标"""
        # 如果没有裁剪框，默认箭头光标
        if self.box_x1 is None:
            self.canvas.config(cursor="arrow")
            return

        # 检查鼠标是否在某个控制点上
        x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
        x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
        cx, cy = (x1+x2)/2, (y1+y2)/2
        half = self.handle_size / 2

        # 9个控制点的屏幕范围
        handle_areas = [
            (x1-half, y1-half, x1+half, y1+half),  # 0 左上
            (cx-half, y1-half, cx+half, y1+half),  # 1 上中
            (x2-half, y1-half, x2+half, y1+half),  # 2 右上
            (x1-half, cy-half, x1+half, cy+half),  # 3 左中
            (cx-half, cy-half, cx+half, cy+half),  # 4 中心
            (x2-half, cy-half, x2+half, cy+half),  # 5 右中
            (x1-half, y2-half, x1+half, y2+half),  # 6 左下
            (cx-half, y2-half, cx+half, y2+half),  # 7 下中
            (x2-half, y2-half, x2+half, y2+half),  # 8 右下
        ]

        # 检查鼠标在哪个控制点上
        for i, (hx1, hy1, hx2, hy2) in enumerate(handle_areas):
            if hx1 <= e.x <= hx2 and hy1 <= e.y <= hy2:
                self.canvas.config(cursor=self.handles[i]["cursor"])
                return

        # 不在控制点上，默认箭头光标
        self.canvas.config(cursor="arrow")

    # ===================== 左键事件：平移地图 + 拖拽控制点 =====================
    def on_left_press(self, e):
        """左键按下：判断是拖拽控制点，还是平移地图"""
        # 如果有裁剪框，先检查是否点中了控制点
        if self.box_x1 is not None:
            x1, y1 = self.ori_to_screen(self.box_x1, self.box_y1)
            x2, y2 = self.ori_to_screen(self.box_x2, self.box_y2)
            cx, cy = (x1+x2)/2, (y1+y2)/2
            half = self.handle_size / 2

            handle_areas = [
                (x1-half, y1-half, x1+half, y1+half),
                (cx-half, y1-half, cx+half, y1+half),
                (x2-half, y1-half, x2+half, y1+half),
                (x1-half, cy-half, x1+half, cy+half),
                (cx-half, cy-half, cx+half, cy+half),
                (x2-half, cy-half, x2+half, cy+half),
                (x1-half, y2-half, x1+half, y2+half),
                (cx-half, y2-half, cx+half, y2+half),
                (x2-half, y2-half, x2+half, y2+half),
            ]

            # 检查是否点中控制点
            for i, (hx1, hy1, hx2, hy2) in enumerate(handle_areas):
                if hx1 <= e.x <= hx2 and hy1 <= e.y <= hy2:
                    self.dragging_handle = i
                    self.drag_start_ori_x, self.drag_start_ori_y = self.screen_to_ori(e.x, e.y)
                    self.drag_start_box = (self.box_x1, self.box_y1, self.box_x2, self.box_y2)
                    return

        # 没点中控制点，进入平移模式
        self.is_panning = True
        self.last_mouse_x = e.x
        self.last_mouse_y = e.y

    def on_left_drag(self, e):
        """左键拖动：拖拽控制点 或 平移地图"""
        # 正在拖拽控制点
        if self.dragging_handle is not None:
            current_ori_x, current_ori_y = self.screen_to_ori(e.x, e.y)
            dx = current_ori_x - self.drag_start_ori_x
            dy = current_ori_y - self.drag_start_ori_y
            x1, y1, x2, y2 = self.drag_start_box

            # 根据拖拽的控制点ID，更新框的坐标
            handle_id = self.dragging_handle
            if handle_id == 0:  # 左上
                new_x1, new_y1 = x1 + dx, y1 + dy
                self.box_x1 = min(new_x1, x2 - 10)
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 1:  # 上中
                new_y1 = y1 + dy
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 2:  # 右上
                new_x2, new_y1 = x2 + dx, y1 + dy
                self.box_x2 = max(new_x2, x1 + 10)
                self.box_y1 = min(new_y1, y2 - 10)
            elif handle_id == 3:  # 左中
                new_x1 = x1 + dx
                self.box_x1 = min(new_x1, x2 - 10)
            elif handle_id == 4:  # 中心：移动整个框
                self.box_x1 = x1 + dx
                self.box_y1 = y1 + dy
                self.box_x2 = x2 + dx
                self.box_y2 = y2 + dy
            elif handle_id == 5:  # 右中
                new_x2 = x2 + dx
                self.box_x2 = max(new_x2, x1 + 10)
            elif handle_id == 6:  # 左下
                new_x1, new_y2 = x1 + dx, y2 + dy
                self.box_x1 = min(new_x1, x2 - 10)
                self.box_y2 = max(new_y2, y1 + 10)
            elif handle_id == 7:  # 下中
                new_y2 = y2 + dy
                self.box_y2 = max(new_y2, y1 + 10)
            elif handle_id == 8:  # 右下
                new_x2, new_y2 = x2 + dx, y2 + dy
                self.box_x2 = max(new_x2, x1 + 10)
                self.box_y2 = max(new_y2, y1 + 10)

            # 限制框不能超出原图边界
            self.box_x1 = max(0, self.box_x1)
            self.box_y1 = max(0, self.box_y1)
            self.box_x2 = min(self.ori_w, self.box_x2)
            self.box_y2 = min(self.ori_h, self.box_y2)

            # 重绘
            self.redraw_all()
            return

        # 正在平移地图
        if self.is_panning:
            dx = e.x - self.last_mouse_x
            dy = e.y - self.last_mouse_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_mouse_x = e.x
            self.last_mouse_y = e.y
            self.redraw_all()

    def on_left_release(self, e):
        """左键松开：结束拖拽/平移"""
        self.dragging_handle = None
        self.is_panning = False

    # ===================== 右键事件：画新的裁剪框 =====================
    def on_right_press(self, e):
        """右键按下：开始画新框"""
        start_ori_x, start_ori_y = self.screen_to_ori(e.x, e.y)
        self.box_x1 = start_ori_x
        self.box_y1 = start_ori_y
        self.box_x2 = start_ori_x
        self.box_y2 = start_ori_y

    def on_right_drag(self, e):
        """右键拖动：实时更新框的大小"""
        end_ori_x, end_ori_y = self.screen_to_ori(e.x, e.y)
        self.box_x2 = end_ori_x
        self.box_y2 = end_ori_y
        self.redraw_all()

    def on_right_release(self, e):
        """右键松开：完成画框，自动生成9个控制点"""
        # 修正框的坐标（确保x1<x2，y1<y2）
        self.box_x1, self.box_x2 = sorted([self.box_x1, self.box_x2])
        self.box_y1, self.box_y2 = sorted([self.box_y1, self.box_y2])
        # 限制框最小尺寸
        if self.box_x2 - self.box_x1 < 10:
            self.box_x2 = self.box_x1 + 10
        if self.box_y2 - self.box_y1 < 10:
            self.box_y2 = self.box_y1 + 10
        # 重绘，显示框和控制点
        self.redraw_all()

    # ===================== 滚轮缩放功能 =====================
    def zoom_at_mouse(self, mouse_x, mouse_y, factor):
        """以鼠标为中心缩放，框和控制点跟着地图一起缩放"""
        ori_x, ori_y = self.screen_to_ori(mouse_x, mouse_y)
        self.current_scale *= factor
        self.current_scale = max(0.1, min(5.0, self.current_scale))
        self.offset_x = mouse_x - (ori_x * self.current_scale)
        self.offset_y = mouse_y - (ori_y * self.current_scale)
        self.redraw_all()

    def zoom_in(self, e):
        self.zoom_at_mouse(e.x, e.y, 1.2)

    def zoom_out(self, e):
        self.zoom_at_mouse(e.x, e.y, 0.8)

    # ===================== 裁剪保存功能 =====================
    def do_crop(self, event):
        """按C键裁剪，保存原图高清分辨率"""
        if self.box_x1 is None:
            print("⚠️  请先右键画框，再按C键裁剪")
            return
        # 修正坐标
        x1 = max(0, int(self.box_x1))
        y1 = max(0, int(self.box_y1))
        x2 = min(self.ori_w, int(self.box_x2))
        y2 = min(self.ori_h, int(self.box_y2))
        # 裁剪并保存
        cropped_img = self.original_img.crop((x1, y1, x2, y2))
        cropped_img.save("燕山大学_裁剪结果.png")
        print(f"✅ 裁剪完成！")
        print(f"📐 裁剪尺寸：{x2-x1} × {y2-y1} 像素")
        print(f"💾 已保存为：燕山大学_裁剪结果.png")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    MapCropper(root, "haigang.png")
    root.mainloop()
