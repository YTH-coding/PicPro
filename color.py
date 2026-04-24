# Copyright (c) 2025 TianhengYe
# Released under the MIT License
# https://opensource.org/license/mit

import tkinter as tk
from tkinter import ttk
import numpy as np
import random
import re

class ColorMapping():
    def __init__(self, parent:tk.Tk, color_data, unique_vals:list[int]=None):
        self.parent = parent
        self.color_data = color_data
        self.dialog = tk.Toplevel(parent)
        self._updating = False  # guard against recursive trace calls

        self.dialog.title("ColorFul")
        self.dialog.configure(bg="#FFFFFF")
        self.dialog.geometry("800x600")
        self.dialog.minsize(800, 600)
        self.dialog.grab_set()  # 模态锁定：弹窗没关就不能操作主窗口

        self.unique_vals = unique_vals
        self.color_mapping = None

        # 设置主题颜色
        self.set_theme()
        
        # 初始化UI
        self.create_widgets()
    
    def set_theme(self):
        """设置应用主题颜色"""
        self.bg_color = "#f0f0f0"
        self.frame_color = "#ffffff"
        self.button_color = "#4a86e8"
        self.button_hover_color = "#3a76d8"
        self.dialog.configure(bg=self.bg_color)
        
        # 设置ttk样式
        style = ttk.Style()
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabelFrame", background=self.bg_color, bordercolor="#ccc")
        style.configure("TLabel", background=self.bg_color)
        style.configure("TButton", background=self.button_color, foreground="#3a76d8")
        style.map("TButton", 
                 background=[("active", self.button_hover_color)],
                 foreground=[("active", "white")])
    
    def create_widgets(self):
        # Main horizontal container
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== Left: Color List ==========
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            left_frame,
            bg="#FFFFFF",
            fg="black",
            font=("Microsoft YaHei", 13),
            relief=tk.SOLID,
            borderwidth=1,
            activestyle=tk.NONE,
            selectbackground="#FFFFFF",
            selectforeground="#aaaaaa",
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.listbox, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.add_initial_colors()
        self.listbox.bind("<<ListboxSelect>>", self.update_color_info)

        # ========== Right: Color Display & Inputs ==========
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- Color preview ---
        self.color_label = tk.Label(
            right_frame,
            text="Color",
            bg="#FFFFFF",
            fg="black",
            font=("Microsoft YaHei", 30),
            anchor=tk.CENTER,
            relief=tk.SOLID,
            borderwidth=1,
            height=4,
        )
        self.color_label.pack(fill=tk.X, pady=(0, 15))

        # --- RGB Sliders ---
        rgb_frame = tk.Frame(right_frame)
        rgb_frame.pack(fill=tk.X, pady=5)

        # Red row
        self.red_val, self.red_label = self._add_slider(rgb_frame, row=0, label_text="红R")
        
        # Green row
        self.green_val, self.green_label = self._add_slider(rgb_frame, row=1, label_text="绿G")

        # Blue row
        self.blue_val, self.blue_label = self._add_slider(rgb_frame, row=2, label_text="蓝B")

        rgb_frame.grid_columnconfigure(1, weight=1)

        # --- HEX row ---
        hex_frame = tk.Frame(right_frame)
        hex_frame.pack(fill=tk.X, pady=5)

        lbl_hex = tk.Label(hex_frame, text="HEX:", font=("Microsoft YaHei", 14))
        lbl_hex.pack(side=tk.LEFT)
        self.entry_hex_var = tk.StringVar()
        self.entry_hex_var.trace_add("write", self.on_hex_changed)
        self.entry_hex = tk.Entry(
            hex_frame, textvariable=self.entry_hex_var,
            font=("Microsoft YaHei", 14), bg="#FFFFFF",
            relief=tk.SOLID, borderwidth=1
        )
        self.entry_hex.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="保存映射关系", width=15,
            command=self.get_data
        ).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="随机生成映射", width=15,
            command=self.random_mapping
        ).grid(row=0, column=1, padx=5)

        canvas = tk.Canvas(right_frame, highlightthickness=0, height=200)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5,0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(5,0))

        # 表头
        ttk.Label(self.inner, text="#").grid(row=0, column=0, padx=5)
        ttk.Label(self.inner, text="数字").grid(row=0, column=1, padx=5)
        ttk.Label(self.inner, text="色彩").grid(row=0, column=2, padx=5)
        ttk.Label(self.inner, text="预览").grid(row=0, column=3, padx=5)

        self.entries = []  # 存储 (序号标签, Entry)
        for number in self.unique_vals:
            self.add_row(number)

    # -------- Event Handlers --------

    def add_row(self, number):
        row = len(self.entries) + 1
        idx = row  # grid 行号（表头占 0）

        lbl = ttk.Label(self.inner, text=str(row), width=5)
        lbl.grid(row=idx, column=0, padx=5, pady=2)

        entry_num = ttk.Entry(self.inner, width=20)
        entry_num.grid(row=idx, column=1, padx=5, pady=2)
        entry_num.insert(0, f"{number}")

        entry_color = ttk.Entry(self.inner, width=17)
        entry_color.grid(row=idx, column=2, padx=5, pady=2)

        # 颜色预览小方块
        preview = tk.Label(self.inner, width=3, height=1, relief=tk.SOLID, borderwidth=1)
        preview.grid(row=idx, column=3, padx=(0, 5), pady=2)
        entry_color.bind("<KeyRelease>", lambda e: self._update_preview(preview, entry_color))

        self.entries.append({
            "row": idx,
            "number": entry_num,
            "color": entry_color,
            "preview": preview,
            "widgets": [lbl, entry_num, entry_color, preview]
        })

    def _update_preview(self, preview, entry):
        color = entry.get().strip()
        if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            preview.configure(bg=color)
        else:
            preview.configure(bg="#FFFFFF")
    
    def get_data(self):
        self.color_mapping = {int(e["number"].get()):str(e["color"].get()) for e in self.entries}
        print("颜色映射已保存")
    
    def random_mapping(self):
        for item in self.entries:
            random_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            item["color"].delete(0, tk.END)
            item["color"].insert(0, random_color)
            self._update_preview(item["preview"], item["color"])

    def _add_slider(self, parent, row, label_text, start=128, from_=0, to=255)->tuple[tk.IntVar, tk.Label]:
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=2)
        var = tk.IntVar(value=start)

        label = ttk.Label(parent, text=str(var.get()))
        label.grid(row=row, column=2, padx=5)

        slider = ttk.Scale(
            parent, from_=from_, to=to, variable=var,
            orient=tk.HORIZONTAL,
            command=lambda _: (label.config(text=str(var.get())),self.on_rgb_changed()) # 这里其实是闭包，滑块数值更新
        )
        slider.grid(row=row, column=1, sticky=tk.EW, padx=(5,5), pady=2)

        ttk.Button(parent, text="-", width=2,
            command=lambda: self.reduce_value(label, var, from_) # 这里其实是闭包
        ).grid(row=row, column=3, padx=(5,0))
        ttk.Button(parent,  text="+", width=2,
            command=lambda: self.increment_value(label, var, to) # 这里其实是闭包
        ).grid(row=row, column=4, padx=(5,0))

        return var, label

    def on_rgb_changed(self, *_args):
        if self._updating:
            return
        self._updating = True

        red = self.red_val.get()
        green = self.green_val.get()
        blue = self.blue_val.get()

        hex_color = f"#{red:02x}{green:02x}{blue:02x}"
        self.entry_hex_var.set(hex_color)
        self.color_label.configure(bg=hex_color, fg=f"#{255-red:02x}{255-green:02x}{255-blue:02x}")

        self.red_label.config(text=str(red))
        self.green_label.config(text=str(green))
        self.blue_label.config(text=str(blue))

        self._updating = False

    def increment_value(self, label_widget, intvar, max_val=255):
        new_val = intvar.get() + 1
        if new_val <= max_val:
            intvar.set(new_val)
        label_widget.config(text=str(intvar.get()))
        self.on_rgb_changed()

    def reduce_value(self, label_widget, intvar, min_val=0):
        new_val = intvar.get() - 1
        if new_val >= min_val:
            intvar.set(new_val)
        label_widget.config(text=str(intvar.get()))
        self.on_rgb_changed()

    def on_hex_changed(self, *_args):
        if self._updating:
            return
        self._updating = True
        try:
            hex_color = self.entry_hex_var.get().strip()
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", hex_color):
                raise ValueError # 如果没有正确输入，将会跳转到后面的except ValueError

            red = int(hex_color[1:3], 16)
            green = int(hex_color[3:5], 16)
            blue = int(hex_color[5:7], 16)

            self.red_val.set(red)
            self.green_val.set(green)
            self.blue_val.set(blue)
            self.red_label.config(text=str(red))
            self.green_label.config(text=str(green))
            self.blue_label.config(text=str(blue))

            self.color_label.configure(bg=hex_color, fg=f"#{255-red:02x}{255-green:02x}{255-blue:02x}")

        except ValueError:
            self.color_label.configure(bg="#FFFFFF", fg="#000000")
        finally:
            self._updating = False

    # -------- Data --------
    def add_initial_colors(self):
        for key, value in self.color_data.items():
            display_text = "{}-{}".format(value["Chinese_name"], key)
            self.listbox.insert(tk.END, display_text)

    def update_color_info(self, _event):
        selection = self.listbox.curselection()
        if not selection:
            return
        whole_name = self.listbox.get(selection[0])
        # split on '-' and take last part as the color key
        name = re.split(r"-", whole_name)[-1]
        color = self.color_data[name]
        self._updating = True
        self.red_val.set(color["RGB"][0])
        self.green_val.set(color["RGB"][1])
        self.blue_val.set(color["RGB"][2])
        self.red_label.config(text=str(color["RGB"][0]))
        self.green_label.config(text=str(color["RGB"][1]))
        self.blue_label.config(text=str(color["RGB"][2]))
        self.entry_hex_var.set(color["HEX"])
        self.color_label.configure(bg=color["HEX"], fg=f'''#{255-color["RGB"][0]:02x}{255-color["RGB"][1]:02x}{255-color["RGB"][2]:02x}''')
        self._updating = False
