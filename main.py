# main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
from core.image_process import ImageProcessor
import json
from sub_ui import ColorMapping, NewPic
import math
from config.convolution import kernels
from typing import Literal
import os
import shutil

class PicPro:
    def __init__(self, root:tk.Tk):
        self.root = root
        self.root.title("YTH的图像处理工具集合")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # 初始化图片变量
        self.original_image = None      # 原始 PIL Image
        self.original_array = None      # 原始 numpy array (RGB)
        self.processed_array = None     # 处理后 numpy array
        
        # 显示用的 PhotoImage 对象（必须保持引用）
        self.original_photo = None
        self.processed_photo = None

        self.color_mapping:dict = None

        self.colormapping_config = {
            "默认颜色定义":"config\color_preset.json",
            "LULC颜色定义":"config\color_preset_landuse.json",
            "马卡龙配色":"config\color_preset_macaron.json",
            "中国传统色":"config\color_preset_chinese.json",
            "日本传统色":"config\color_preset_japanese.json",
            "莫兰迪色系":"config\color_preset_morandi.json",
            "蜡笔色系Pastel":"config\color_preset_Pastel.json"
        }

        self.workingspace = "workingspace"

        self.work_temp_file:dict[str,list[str, Literal["RGB", "L"]]] = {}
        
        self.color_matrix:dict[str, list[list[float]]] = self.json_load("config\color_matrix.json")
        
        self.color_data = self.json_load(self.colormapping_config["默认颜色定义"])
        
        self.kernels = kernels
        
        # 设置主题颜色
        self.set_theme()
        
        # 初始化UI
        self.create_widgets()

        self.process = ImageProcessor()
    
    def json_load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def set_theme(self):
        """设置应用主题颜色"""
        self.bg_color = "#f0f0f0"
        self.frame_color = "#ffffff"
        self.button_color = "#4a86e8"
        self.button_hover_color = "#3a76d8"
        self.root.configure(bg=self.bg_color)
        
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
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        self.create_control_panel(main_frame)
        
        # 右侧绘图区域
        self.create_plot_area(main_frame)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        iobtn_frame = ttk.LabelFrame(left_frame, text="文件", padding=10)
        iobtn_frame.pack(fill=tk.X, pady=5)

        self.file_operate = tk.StringVar(value="文件操作")
        # 获取矩阵名称列表
        self.file_combo = ttk.Combobox(
            iobtn_frame,
            textvariable=self.file_operate,
            values=["新建图片", "打开彩图", "打开灰图","保存图片", "关闭软件"],  # 直接写列表
            state="readonly"
        )
        self.file_combo.pack(fill=tk.X, pady=5)
        
        self.file_combo.bind("<<ComboboxSelected>>", self.on_file_operate_selected)

        self.create_workstream(left_frame)

        control_frame = ttk.LabelFrame(left_frame, text="图像处理控制", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        basebtn_frame = ttk.Frame(control_frame)
        basebtn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(basebtn_frame, text="左转", width=6, 
            command=lambda: self.apply_rotation(clockwise=False)   # 逆时针
        ).grid(row=0, column=0, padx=5)
        ttk.Button(basebtn_frame, text="右转", width=6,
            command=lambda: self.apply_rotation(clockwise=True)    # 顺时针
        ).grid(row=0, column=1, padx=5)
        ttk.Button(basebtn_frame, text="反相", width=6,
            command=self.apply_reverse
        ).grid(row=0, column=2, padx=5)
        ttk.Button(basebtn_frame, text="复位", width=6,
            command=self.set_original
        ).grid(row=0, column=3, padx=5)

        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.X, pady=5)

        bin_frame = self.create_binarization_settings(notebook)
        notebook.add(bin_frame, text="二值化")

        gray_frame = self.create_rgb2gray_settings(notebook)
        notebook.add(gray_frame, text="灰度化")

        clean_frame = self.create_colorclean_settings(notebook)
        notebook.add(clean_frame, text="净色化")

        self.create_colormatrix(control_frame) # 颜色矩阵

        self.create_gray2rgb_setting(control_frame)

        self.create_convolution(control_frame) # 卷积操作
    
    def on_file_operate_selected(self, event):
        choice = self.file_combo.get()
        if choice == "新建图片":
            self.new_pic()
        elif choice == "打开彩图":
            self.load_image(mode="RGB")
        elif choice == "打开灰图":
            self.load_image(mode="L")
        elif choice == "保存图片":
            self.save_result()
        elif choice == "退出":
            self.root.destroy()
        
    def new_pic(self):
        dialog_new_pic = NewPic(self.root)
        dialog_new_pic.dialog.wait_window()

        try:
            img_array = dialog_new_pic.original_array
            
            the_times = int(math.floor(min(600/img_array.shape[0], 600/img_array.shape[1])))
            self.original_array = np.kron(img_array, np.ones((the_times, the_times),dtype=int)).astype(np.uint8)

            self.display_image(self.original_array, self.original_label, is_original=True)
        except:
            print("未能生成图片")
            pass
    
    def create_binarization_settings(self, parent)->tk.LabelFrame:

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        # 第0行：灰度边界
        self.binarization_gray_var, self.binarization_gray_label = self._add_slider(frame, row=0, label_text="灰度G")

        # 第1行：红色边界
        self.binarization_red_var, self.binarization_red_label = self._add_slider(frame, row=1, label_text="红色G")

        # 第2行：绿色边界
        self.binarization_green_var, self.binarization_green_label = self._add_slider(frame, row=2, label_text="绿色G")

        # 第3行：蓝色边界
        self.binarization_blue_var, self.binarization_blue_label = self._add_slider(frame, row=3, label_text="蓝色B")

        ttk.Button(frame, text="√ 灰度图二值化,RGB参数无用", width=2, command=self.apply_binarization).grid(row=4, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        return frame      

    def create_rgb2gray_settings(self, parent)->tk.LabelFrame:

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        # 第1行：红色边界
        self.rgb2gray_red_var, self.rgb2gray_red_label = self._add_slider(frame, row=0, label_text="红色R",start=76)

        # 第2行：绿色边界
        self.rgb2gray_green_var, self.rgb2gray_green_label = self._add_slider(frame, row=1, label_text="绿色G",start=150)

        # 第3行：蓝色边界
        self.rgb2gray_blue_var, self.rgb2gray_blue_label = self._add_slider(frame, row=2, label_text="蓝色B",start=29)
        
        ttk.Button(frame, text="√ 默认红76,绿150,蓝29,等比例无变化", width=2, command=self.apply_grayscale).grid(row=3, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        return frame

    def create_colorclean_settings(self, parent)->tk.LabelFrame:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)

        # 第1行：二值化边界
        self.colorclean_binbonud_var, self.colorclean_binbonud_label = self._add_slider(frame, row=0, label_text="二值边界")

        # 第2行：红色起始
        self.colorclean_redbound_thresh, self.colorclean_redbound_label = self._add_slider(frame, row=1, label_text="红色起始")

        # 第3行：红色色差
        self.colorclean_reddiff_var, self.colorclean_reddiff_label = self._add_slider(frame, row=2, label_text="红色色差")

        ttk.Button(frame, text="√ 用于文件扫描处理", width=2, command=self.apply_clean_color).grid(row=3, column=0, columnspan=5, sticky=tk.EW, padx=5, pady=5)

        return frame

    def create_colormatrix(self, parent):
        frame = ttk.LabelFrame(parent, text="颜色矩阵-滤镜", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.chart_type = tk.StringVar(value="选择滤镜")
        
        # 获取矩阵名称列表
        chart_types = list(self.color_matrix.keys())
        
        chart_combo = ttk.Combobox(
            frame, 
            textvariable=self.chart_type, 
            values=chart_types, 
            state="readonly"
        )
        chart_combo.pack(fill=tk.X, pady=5)
        
        # 绑定选择事件
        chart_combo.bind("<<ComboboxSelected>>", self.on_matrix_selected)
    
    def on_matrix_selected(self, event=None):
        """当选择颜色矩阵时调用"""
        selected = self.chart_type.get()
        matrix = self.color_matrix.get(selected)
        if matrix:
            # 调用颜色矩阵处理函数
            self.apply_color_matrix(matrix)
        
    def create_gray2rgb_setting(self, parent):
        frame = ttk.LabelFrame(parent, text="伪彩色处理", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.colormapping_type = tk.StringVar(value="选择颜色映射组")
        
        # 获取矩阵名称列表
        colormapping_types = list(self.colormapping_config.keys())
        
        colormapping_combo = ttk.Combobox(
            frame, 
            textvariable=self.colormapping_type, 
            values=colormapping_types, 
            state="readonly"
        )
        colormapping_combo.pack(fill=tk.X, pady=5)
        
        # 绑定选择事件
        colormapping_combo.bind("<<ComboboxSelected>>", self.on_colormapping_selected)

        ttk.Button(frame, text="进行伪彩色化设置", width=9,
            command=self.gray2color
        ).pack(fill=tk.X, pady=5)
    
    def on_colormapping_selected(self, event=None):
        selected = self.colormapping_type.get()
        if selected:
            self.color_data = self.json_load(self.colormapping_config[selected])
            print(f"颜色映射组更换为 {selected} ")
    
    def create_convolution(self, parent):
        frame = ttk.LabelFrame(parent, text="卷积操作", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.kernels_type = tk.StringVar(value="选择卷积核")
        
        # 获取矩阵名称列表
        kernels_types = list(self.kernels.keys())
        
        kernels_combo = ttk.Combobox(
            frame, 
            textvariable=self.kernels_type, 
            values=kernels_types, 
            state="readonly"
        )
        kernels_combo.pack(fill=tk.X, pady=5)
        
        # 绑定选择事件
        kernels_combo.bind("<<ComboboxSelected>>", self.on_kernels_selected)
    
    def on_kernels_selected(self, event=None):
        selected = self.kernels_type.get()
        kernels = self.kernels.get(selected)
        if kernels:
            # 调用颜色矩阵处理函数
            self.apply_convolution(kernels)
    
    def create_workstream(self, parent):
        frame = ttk.LabelFrame(parent, text="工作流", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.work_type = tk.StringVar(value="暂存文件")
        
        try:
            # 获取矩阵名称列表
            work_types = list(self.work_temp_file.keys())
        except AttributeError:
            work_types = []
        
        self.work_combo = ttk.Combobox(
            frame, 
            textvariable=self.work_type, 
            values=work_types, 
            state="readonly"
        )
        self.work_combo.pack(fill=tk.X, pady=5)
        
        # 绑定选择事件
        self.work_combo.bind("<<ComboboxSelected>>", self.on_temp_file_selected)

        basebtn_frame = ttk.Frame(frame)
        basebtn_frame.pack(fill=tk.X, pady=5)
        basebtn_frame.columnconfigure(0, weight=1)
        basebtn_frame.columnconfigure(1, weight=1)

        root.bind_all("<Return>", lambda e: self.save_result(temp_file=True))

        ttk.Button(basebtn_frame, text="Enter暂存", width=9,
            command=lambda:self.save_result(temp_file=True)
        ).grid(row=0, column=0, padx=5)
        ttk.Button(basebtn_frame, text="清空暂存", width=9,
            command=self.work_temp_file_clear
        ).grid(row=0, column=1, padx=5)
    
    def on_temp_file_selected(self, event=None):
        selected = self.work_type.get()
        info = self.work_temp_file.get(selected)
        if info:
            self.load_image(mode=info[1], file_path=info[0])
    
    def work_temp_file_clear(self):
        messagebox.showwarning("警告", "此操作清空工作目录")
        shutil.rmtree(self.workingspace)
        os.makedirs(self.workingspace)
        if self.work_temp_file:
            self.work_temp_file.clear()
            self.work_combo['values'] = []
    
    def gray2color(self):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        if self.original_array.ndim != 2:
            messagebox.showwarning("警告", "本操作仅能处理灰度图")
            return
        
        unique_vals = np.unique(self.original_array).tolist()
        dialog_color_mapping = ColorMapping(self.root, self.color_data, unique_vals)
        dialog_color_mapping.dialog.wait_window()

        try:
            self.color_mapping = dialog_color_mapping.color_mapping
            self.processed_array = self.process.gray2color(self.original_array, self.color_mapping)
            self.display_image(self.processed_array, self.result_label, is_original=False)
        except:
            print("未能设置颜色映射")
            pass
    
    def _add_slider(self, parent, row, label_text, start=128, from_=0, to=255)->tuple[tk.IntVar, tk.Label]:
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
        """创建图片显示区域（修改：增加固定尺寸和滚动条）"""
        control_frame = ttk.LabelFrame(parent, text="图片显示区域", padding=5)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_pic_show(control_frame)
    
    def create_pic_show(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        original_frame = ttk.LabelFrame(control_frame, text="原图", padding=5)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_label = ttk.Label(original_frame, background="#ffffff", relief="sunken")
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        # 处理后区域
        result_frame = ttk.LabelFrame(control_frame, text="处理后", padding=5)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.result_label = ttk.Label(result_frame, background="#ffffff", relief="sunken")
        self.result_label.pack(fill=tk.BOTH, expand=True)
    
    def load_image(self, mode="RGB", file_path=None):
        """加载图片文件"""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="选择图片",
                filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("所有文件", "*.*")]
            )
            if not file_path:
                return
        
        try:
            # 打开并转为 RGB
            self.original_image = Image.open(file_path).convert(mode=mode)
            self.original_array = np.array(self.original_image)
            
            # 显示原图
            self.display_image(self.original_array, self.original_label, is_original=True)
            
            # 清空处理结果
            self.processed_array = None
            self.display_image(None, self.result_label, is_original=False)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片：{e}")
    
    def display_image(self, img_array, label_widget, is_original=True, max_width=700, max_height=700):
        """显示 numpy 数组图片到 Label，自动缩放并保持比例"""
        if img_array is None:
            label_widget.config(image='')
            if is_original:
                self.original_photo = None
            else:
                self.processed_photo = None
            return
        
        # 将 numpy 数组转为 PIL Image
        if img_array.dtype == np.uint8 and img_array.ndim == 3:
            pil_img = Image.fromarray(img_array)
        elif img_array.dtype == np.uint8 and img_array.ndim == 2:
            pil_img = Image.fromarray(np.stack([img_array, img_array, img_array], axis=2))
        else:
            raise ValueError("不支持的图片格式")
        
        # 计算缩放尺寸
        w, h = pil_img.size
        ratio = min(max_width / w, max_height / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 转换为 PhotoImage
        photo = ImageTk.PhotoImage(resized)
        
        # 更新 Label
        label_widget.config(image=photo)
        # 保持引用
        if is_original:
            self.original_photo = photo
        else:
            self.processed_photo = photo
    
    def apply_clean_color(self):
        """净色处理：白底黑字红章"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        if self.original_array.ndim != 3:
            messagebox.showwarning("警告", "这不是RGB彩色图片")
            return
        bin_bound = self.colorclean_binbonud_var.get()   # 灰度二值化阈值
        red_start = self.colorclean_redbound_thresh.get()   # 红色通道最小值
        red_diff = self.colorclean_reddiff_var.get()     # R-G和R-B差值阈值
        
        self.processed_array = self.process.document_clean(
            self.original_array,
            red_r_thresh=red_start,
            red_diff_thresh=red_diff,
            gray_thresh=bin_bound
        )
        
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_rotation(self, clockwise=True):
        """旋转图片（顺时针或逆时针90度）"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        # 注意：旋转应该基于原始图还是当前处理图？简单起见基于原始图
        source = self.original_array
        if clockwise:
            rotated = self.process.rotate_90(source, clockwise=True)
        else:
            rotated = self.process.rotate_90(source, clockwise=False)
        self.processed_array = rotated
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_reverse(self):
        """反转颜色"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        reversed_img = self.process.reversed(self.original_array)
        self.processed_array = reversed_img
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def set_original(self):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        self.processed_array = self.original_array
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_grayscale(self):
        """灰度化（使用当前RGB权重滑块）"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        if self.original_array.ndim != 3:
            messagebox.showwarning("警告", "这不是RGB彩色图片")
            return
        r_w = self.rgb2gray_red_var.get() / 255.0   # 滑块值是整数0-255，转为权重
        g_w = self.rgb2gray_green_var.get() / 255.0
        b_w = self.rgb2gray_blue_var.get() / 255.0
        # 归一化权重和=1
        total = r_w + g_w + b_w
        if total != 0:
            r_w /= total
            g_w /= total
            b_w /= total
        self.processed_array = self.process.rgb2gray(self.original_array, weights=(r_w, g_w, b_w))
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_binarization(self):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        gray = self.binarization_gray_var.get()
        r_w = self.binarization_red_var.get() / 255.0   # 滑块值是整数0-255，转为权重
        g_w = self.binarization_green_var.get() / 255.0
        b_w = self.binarization_blue_var.get() / 255.0
        total = r_w + g_w + b_w
        if total != 0:
            r_w /= total
            g_w /= total
            b_w /= total
        self.processed_array = self.process.binarization(self.original_array, bound=gray, weights=(r_w, g_w, b_w))
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_color_matrix(self, matrix):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        if self.original_array.ndim != 3:
            messagebox.showwarning("警告", "这不是RGB彩色图片")
            return
        self.processed_array = self.process.color_matrix(self.original_array, matrix)
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_convolution(self, kernel):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        self.processed_array = self.process.convolution_std(self.original_array, kernel)
        self.display_image(self.processed_array, self.result_label, is_original=False)
        
    def save_result(self, temp_file=False):
        """保存处理后的图片"""
        if self.processed_array is None:
            messagebox.showwarning("警告", "没有处理结果可保存")
            return
        if temp_file:

            self.original_array = self.processed_array
            self.display_image(self.original_array, self.original_label, is_original=True)

            temp_id = len(self.work_temp_file)
            file_path = f"{self.workingspace}/temp{temp_id}.png"
            if self.processed_array.ndim == 2:
                self.work_temp_file[f"temp{temp_id}"] = [file_path, "L"]
            elif self.processed_array.ndim == 3:
                self.work_temp_file[f"temp{temp_id}"] = [file_path, "RGB"]
            self.work_combo['values'] = list(self.work_temp_file.keys())
            print(self.work_temp_file)
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("JPEG图片", "*.jpg"), ("所有文件", "*.*")]
            )
        if file_path:
            if self.processed_array.ndim == 2:
                Image.fromarray(self.processed_array, mode="L").save(file_path)
            elif self.processed_array.ndim == 3:
                Image.fromarray(self.processed_array, mode="RGB").save(file_path)
            if temp_file:
                pass
            else:
                messagebox.showinfo(f"成功保存,图片通道为{self.processed_array.ndim}", f"图片已保存到：{file_path}")
if __name__ == "__main__":
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    app = PicPro(root)
    root.mainloop()