# newpic.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import math

class NewPic():
    def __init__(self, parent:tk.Tk):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self._updating = False  # guard against recursive trace calls

        self.dialog.title("NewPic")
        self.dialog.configure(bg="#FFFFFF")
        self.dialog.geometry("900x600")
        self.dialog.minsize(900, 600)
        self.dialog.grab_set()  # 模态锁定：弹窗没关就不能操作主窗口

        self.original_image = None      # 原始 PIL Image
        self.original_array = None      # 原始 numpy array (RGB)
        
        # 显示用的 PhotoImage 对象（必须保持引用）
        self.original_photo = None

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
        """创建应用界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        self.create_control_panel(main_frame)
        
        # 右侧绘图区域
        self.create_plot_area(main_frame)
    
    def create_control_panel(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, fill=tk.Y)

        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        ttk.Button(frame, text="生成", width=9,
            command=self.generate
        ).grid(row=0, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        self.width_var, self.width_label = self._add_slider(frame, row=1, label_text="宽", start=10, from_=1, to=200)
        self.height_var, self.height_label = self._add_slider(frame, row=2, label_text="高", start=10, from_=1, to=200)

        self.operate = tk.StringVar(value="其他参数")
        # 获取矩阵名称列表
        self.combo = ttk.Combobox(
            frame,
            textvariable=self.operate,
            values=["百分比", "比例值"],  # 直接写列表
            state="readonly"
        )
        self.combo.grid(row=3, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        self.combo.bind("<<ComboboxSelected>>", self.get_choice)

        frame.rowconfigure(5, weight=1)

        # 新增行按钮
        ttk.Button(frame, text="+ 新增行", command=self.add_row).grid(row=4, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        # 滚动区域
        canvas = tk.Canvas(frame, highlightthickness=0, height=200, width=300)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_mw(_=None):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mw(_=None):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mw)
        canvas.bind("<Leave>", _unbind_mw)
        self.inner.bind("<Enter>", _bind_mw)
        self.inner.bind("<Leave>", _unbind_mw)

        canvas.grid(row=5, column=0, columnspan=5, sticky=tk.NSEW, pady=(5,0))
        scrollbar.grid(row=5, column=4, sticky=tk.NS, pady=(5,0))

        # 表头
        ttk.Label(self.inner, text="#").grid(row=0, column=0, padx=5)
        ttk.Label(self.inner, text="数字").grid(row=0, column=1, padx=5)
        ttk.Label(self.inner, text="比例值").grid(row=0, column=2, padx=5)
        ttk.Label(self.inner, text="").grid(row=0, column=3, padx=5)

        self.entries = []  # 存储 (序号标签, Entry, 删除按钮)
        for _ in range(3):
            self.add_row()

    def add_row(self):
        row = len(self.entries) + 1
        idx = row  # grid 行号（表头占 0）

        lbl = ttk.Label(self.inner, text=str(row), width=1)
        lbl.grid(row=idx, column=0, padx=5, pady=2)

        number = ttk.Entry(self.inner, width=10)
        number.grid(row=idx, column=1, padx=5, pady=2)
        number.insert(0, f"{row}")

        p = ttk.Entry(self.inner, width=10)
        p.grid(row=idx, column=2, padx=5, pady=2)
        # p.insert(0, f"{row}")

        del_btn = ttk.Button(self.inner, text="✕", width=2,
                             command=lambda r=idx: self._del_row(r))
        del_btn.grid(row=idx, column=3, padx=5)

        self.entries.append({
            "row": idx,
            "number": number,
            "p":p,
            "widgets": [lbl, number,p, del_btn]
        })

    def _del_row(self, row_idx):
        for item in self.entries[:]:
            if item["row"] == row_idx:
                for w in item["widgets"]:
                    w.destroy()
                self.entries.remove(item)
    
    def generate(self):
        width = self.width_var.get()
        height = self.height_var.get()
        result_old =  {int(e["number"].get())%256:int(e["p"].get()) for e in self.entries}

        choice = self.get_choice()
        if choice == "百分比":
            result = {k:i/100 for k,i in result_old.items()}
            if sum(result.values())>1:
                return
        elif choice == "比例值":
            total = sum(result_old.values())
            result = {k:i/total for k,i in result_old.items()}
        else:
            return

        if 255 not in result_old:
            result[255] = 1-sum(result.values())
        else:
            result[255] = 1+result[255]-sum(result.values())

        self.original_array = np.random.choice(list(result.keys()), size = (width, height), p=list(result.values())).astype(np.uint8)

        the_times = int(math.floor(min(600/width, 600/height)))
        img_array = np.kron(self.original_array, np.ones((the_times, the_times),dtype=int)).astype(np.uint8)

        self.display_image(img_array, self.original_label)

    def get_choice(self, event=None):
        return self.operate.get()

    def _add_slider(self, parent, row, label_text, start=128, from_=0, to=200)->tuple[tk.IntVar, tk.Label]:
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=2)
        var = tk.IntVar(value=start)

        label = ttk.Label(parent, text=str(var.get()))
        label.grid(row=row, column=2, padx=5)

        slider = ttk.Scale(
            parent, from_=from_, to=to, variable=var,
            orient=tk.HORIZONTAL,
            command=lambda _: label.config(text=str(var.get())) # 这里其实是闭包，滑块数值更新
        )
        slider.grid(row=row, column=1, sticky=tk.EW, padx=(5,5), pady=2)

        ttk.Button(parent, text="-", width=2,
            command=lambda: self.reduce_value(label, var, from_) # 这里其实是闭包
        ).grid(row=row, column=3, padx=(5,0))
        ttk.Button(parent,  text="+", width=2,
            command=lambda: self.increment_value(label, var, to) # 这里其实是闭包
        ).grid(row=row, column=4, padx=(5,0))

        return var, label

    def increment_value(self, label_widget:tk.Label, intvar:tk.IntVar, max_val=255):
        new_val = intvar.get() + 1
        if new_val <= max_val:
            intvar.set(new_val)
        label_widget.config(text=str(intvar.get()))

    def reduce_value(self, label_widget:tk.Label, intvar:tk.IntVar, min_val=0):
        new_val = intvar.get() - 1
        if new_val >= min_val:
            intvar.set(new_val)
        label_widget.config(text=str(intvar.get()))

    def create_plot_area(self, parent):
        original_frame = ttk.LabelFrame(parent, text="原图", padding=5)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_label = ttk.Label(original_frame, background="#ffffff", relief="sunken")
        self.original_label.pack(fill=tk.BOTH, expand=True)
    
    def display_image(self, img_array:np.ndarray, label_widget:ttk.Label):
        """显示 numpy 数组图片到 Label，自动缩放并保持比例"""
        if img_array is None:
            label_widget.config(image='')
            self.original_photo = None
            return
        
        # 将 numpy 数组转为 PIL Image
        # print((img_array.dtype == np.uint8), (img_array.ndim == 2))
        pil_img = Image.fromarray(np.stack([img_array, img_array, img_array], axis=2))

        # 转为 tkinter 可显示的 PhotoImage
        photo = ImageTk.PhotoImage(pil_img)

        # 更新 Label
        label_widget.config(image=photo)
        # 保持引用（否则会被垃圾回收）
        self.original_photo = photo