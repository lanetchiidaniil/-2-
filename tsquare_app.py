"""Tkinter interface and camera animation for the T-square fractal."""
import tkinter as tk

from fractal import render_fractal
from palettes import PALETTES, level_color

MAX_DEPTH = 7


class TSquareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Геометрический фрактал — Т-квадрат")
        self.root.geometry("1100x760")
        self.root.minsize(760, 520)
        self.depth = 4
        self.zoom = 1.0
        self.pan_x = self.pan_y = 0.0
        self.palette_name = tk.StringVar(value="Неон")
        self.rainbow = tk.BooleanVar(value=False)
        self.auto_zoom = False
        self.reveal_progress = 0.0
        self.color_phase = 0.0

        self.sidebar = tk.Frame(root, width=220, bg="#182033", padx=14, pady=16)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="Т-КВАДРАТ", font=("Segoe UI", 15, "bold"),
                 bg="#182033", fg="white").pack(anchor="w", pady=(0, 18))
        tk.Label(self.sidebar, text="Глубина рекурсии", font=("Segoe UI", 10),
                 bg="#182033", fg="#cbd5e1").pack(anchor="w")
        depth_row = tk.Frame(self.sidebar, bg="#182033")
        depth_row.pack(fill=tk.X, pady=(7, 18))
        tk.Button(depth_row, text="−", width=4,
                  command=lambda: self.change_depth(-1)).pack(side=tk.LEFT)
        self.depth_label = tk.Label(depth_row, text=str(self.depth), width=5,
                                    bg="#182033", fg="white",
                                    font=("Segoe UI", 12, "bold"))
        self.depth_label.pack(side=tk.LEFT)
        tk.Button(depth_row, text="+", width=4,
                  command=lambda: self.change_depth(1)).pack(side=tk.LEFT)

        tk.Label(self.sidebar, text="Цветовая гамма", font=("Segoe UI", 10),
                 bg="#182033", fg="#cbd5e1").pack(anchor="w", pady=(0, 7))
        for name, colors in PALETTES.items():
            row = tk.Frame(self.sidebar, bg="#182033")
            row.pack(fill=tk.X, pady=2)
            tk.Radiobutton(row, text=name, variable=self.palette_name, value=name,
                           command=self.draw, bg="#182033", fg="white",
                           selectcolor="#303b52", activebackground="#182033",
                           activeforeground="white").pack(side=tk.LEFT)
            for color in colors:
                tk.Label(row, bg=color, width=2, height=1).pack(side=tk.LEFT, padx=1)

        tk.Checkbutton(self.sidebar, text="Переливание цветов", variable=self.rainbow,
                       command=self.draw, bg="#182033", fg="white",
                       selectcolor="#303b52", activebackground="#182033",
                       activeforeground="white").pack(anchor="w", pady=(14, 10))
        self.auto_button = tk.Button(self.sidebar, text="▶ Иллюзия приближения",
                                     command=self.toggle_auto_zoom,
                                     wraplength=175, pady=8)
        self.auto_button.pack(fill=tk.X, pady=(4, 8))
        tk.Button(self.sidebar, text="Сбросить масштаб",
                  command=self.reset_view).pack(fill=tk.X, pady=4)
        tk.Label(self.sidebar,
                 text="Колесо мыши — масштаб\n+ / − или ↑ / ↓ — глубина\nМаксимум: N = 7",
                 font=("Segoe UI", 9), bg="#182033", fg="#aab6cc",
                 justify=tk.LEFT).pack(anchor="w", side=tk.BOTTOM, pady=8)

        main_area = tk.Frame(root, bg="#101522")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(main_area, background="#080b18", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        self.info = tk.StringVar()
        tk.Label(main_area, textvariable=self.info, font=("Segoe UI", 10),
                 bg="#20293a", fg="white", pady=8).pack(fill=tk.X, padx=10, pady=(0, 8))

        self.canvas.bind("<Configure>", lambda _event: self.draw())
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda event: self.zoom_at(event.x, event.y, 1.15))
        self.canvas.bind("<Button-5>", lambda event: self.zoom_at(event.x, event.y, 1/1.15))
        for key in ("<KeyPress-plus>", "<KeyPress-equal>", "<KeyPress-KP_Add>", "<Up>"):
            self.root.bind(key, lambda _event: self.change_depth(1))
        for key in ("<KeyPress-minus>", "<KeyPress-KP_Subtract>", "<Down>"):
            self.root.bind(key, lambda _event: self.change_depth(-1))
        self.root.bind("<KeyPress-0>", lambda _event: self.reset_view())
        self.draw()
        self.root.after(100, self.animate_colors)

    def change_depth(self, delta):
        self.depth = max(0, min(MAX_DEPTH, self.depth + delta))
        self.depth_label.config(text=str(self.depth))
        self.reveal_progress = 0.0
        self.draw()

    def reset_view(self):
        self.zoom = 1.0
        self.pan_x = self.pan_y = 0.0
        self.draw()

    def on_mouse_wheel(self, event):
        self.zoom_at(event.x, event.y, 1.15 if event.delta > 0 else 1/1.15)

    def zoom_at(self, x, y, factor):
        factor = max(1/1.15, min(1.15, factor))
        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        self.pan_x = x-cx-(x-cx-self.pan_x)*factor
        self.pan_y = y-cy-(y-cy-self.pan_y)*factor
        self.zoom = max(0.15, min(30.0, self.zoom*factor))
        self.draw()

    def toggle_auto_zoom(self):
        self.auto_zoom = not self.auto_zoom
        self.auto_button.config(text="■ Остановить приближение" if self.auto_zoom
                                else "▶ Иллюзия приближения")
        if self.auto_zoom:
            self.animate_zoom()

    def animate_zoom(self):
        if not self.auto_zoom:
            return
        # Масштаб меняется вокруг фиксированного центра холста. Панорамирование
        # не пересчитывается, поэтому изображение не уплывает по диагонали.
        self.zoom = min(30.0, self.zoom * 1.018)
        if self.depth < MAX_DEPTH:
            self.reveal_progress += 0.035
            if self.reveal_progress >= 1.0:
                self.depth += 1
                self.depth_label.config(text=str(self.depth))
                self.reveal_progress = 0.0
        if self.rainbow.get():
            self.color_phase = (self.color_phase + 0.012) % 1.0
        self.draw()
        if self.zoom >= 30.0:
            self.auto_zoom = False
            self.auto_button.config(text="▶ Иллюзия приближения")
            return
        delay = 65 if self.depth >= 6 else 40
        self.root.after(delay, self.animate_zoom)

    def animate_colors(self):
        if self.rainbow.get() and not self.auto_zoom:
            self.color_phase = (self.color_phase + 0.018) % 1.0
            self.draw()
        self.root.after(100, self.animate_colors)

    def color_for_level(self, level):
        return level_color(level, self.palette_name.get(),
                           self.rainbow.get(), self.color_phase)

    def draw(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 2 or height < 2:
            return

        center_x = width / 2 + self.pan_x
        center_y = height / 2 + self.pan_y
        side = min(width, height) / 3.2 * self.zoom
        ppm_data, count = render_fractal(
            width, height, center_x, center_y, side, self.depth,
            self.color_for_level, self.reveal_progress, MAX_DEPTH
        )
        self.fractal_image = tk.PhotoImage(data=ppm_data, format="PPM")
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.fractal_image, anchor="nw")
        mode = "переливание включено" if self.rainbow.get() else self.palette_name.get()
        self.info.set(f"Глубина N = {self.depth}  |  Квадратов: {count}  |  "
                      f"Палитра: {mode}  |  Zoom: {self.zoom:.2f}×")


