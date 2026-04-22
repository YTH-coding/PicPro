import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
from test_c.image_process import ImageProcessor
import json

class PicPro:
    def __init__(self, root):
        self.root = root
        self.root.title("YTH的图像处理工具集合")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # 初始化图片变量
        self.original_image = None      # 原始 PIL Image
        self.original_array = None      # 原始 numpy array (RGB)
        self.processed_array = None     # 处理后 numpy array
        
        # 显示用的 PhotoImage 对象（必须保持引用）
        self.original_photo = None
        self.processed_photo = None

        with open("config\color_matrix.json", 'r', encoding='utf-8') as f:
            self.color_matrix:dict[str, list[list[float]]] = json.load(f)
        
        # 设置主题颜色
        self.set_theme()
        
        # 初始化UI
        self.create_widgets()

        self.process = ImageProcessor()

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
        control_frame = ttk.LabelFrame(parent, text="图像处理控制", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 旋转
        self.create_rotate_bottons(control_frame)

        # 二值化
        self.create_binarization_settings(control_frame)

        # 反转
        self.create_reversed_botton(control_frame)

        # 灰度化
        self.create_rgb2gray_settings(control_frame)

        # 净色
        self.create_colorclean_settings(control_frame)

        # 伪彩色
        # self.create_gray2rgb_settings(control_frame)

        # 颜色矩阵
        self.create_colormatrix(control_frame)
    
    def create_rotate_bottons(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            frame, 
            text="左转90度", 
            command=lambda: self.apply_rotation(clockwise=False)   # 逆时针
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame, 
            text="右转90度", 
            command=lambda: self.apply_rotation(clockwise=True)    # 顺时针
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_binarization_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="颜色与二值化阈值", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        # 第0行：灰度边界
        ttk.Label(frame, text="灰度G").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.binarization_gray_thresh = tk.IntVar(value=128)  # 初始128更合理
        gray_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.binarization_gray_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.binarization_gray_thresh_label, self.binarization_gray_thresh)
        )
        gray_slider.grid(row=0, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.binarization_gray_thresh_label = ttk.Label(frame, text=str(self.binarization_gray_thresh.get()))
        self.binarization_gray_thresh_label.grid(row=0, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.binarization_gray_thresh_label, self.binarization_gray_thresh, 0)
        ).grid(row=0, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.binarization_gray_thresh_label, self.binarization_gray_thresh, 255)
        ).grid(row=0, column=4, padx=(5,0))

        # 第1行：红色边界
        ttk.Label(frame, text="红色R").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.binarization_red_thresh = tk.IntVar(value=200)
        red_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.binarization_red_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.binarization_red_thresh_label, self.binarization_red_thresh)
        )
        red_slider.grid(row=1, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.binarization_red_thresh_label = ttk.Label(frame, text=str(self.binarization_red_thresh.get()))
        self.binarization_red_thresh_label.grid(row=1, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.binarization_red_thresh_label, self.binarization_red_thresh, 0)
        ).grid(row=1, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.binarization_red_thresh_label, self.binarization_red_thresh, 255)
        ).grid(row=1, column=4, padx=(5,0))

        # 第2行：绿色边界
        ttk.Label(frame, text="绿色G").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.binarization_green_thresh = tk.IntVar(value=50)
        green_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.binarization_green_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.binarization_green_thresh_label, self.binarization_green_thresh)
        )
        green_slider.grid(row=2, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.binarization_green_thresh_label = ttk.Label(frame, text=str(self.binarization_green_thresh.get()))
        self.binarization_green_thresh_label.grid(row=2, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.binarization_green_thresh_label, self.binarization_green_thresh, 0)
        ).grid(row=2, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.binarization_green_thresh_label, self.binarization_green_thresh, 255)
        ).grid(row=2, column=4, padx=(5,0))

        # 第3行：蓝色边界
        ttk.Label(frame, text="蓝色B").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.binarization_blue_thresh = tk.IntVar(value=50)
        blue_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.binarization_blue_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.binarization_blue_thresh_label, self.binarization_blue_thresh)
        )
        blue_slider.grid(row=3, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.binarization_blue_thresh_label = ttk.Label(frame, text=str(self.binarization_blue_thresh.get()))
        self.binarization_blue_thresh_label.grid(row=3, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.binarization_blue_thresh_label, self.binarization_blue_thresh, 0)
        ).grid(row=3, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.binarization_blue_thresh_label, self.binarization_blue_thresh, 255)
        ).grid(row=3, column=4, padx=(5,0))

    def create_reversed_botton(self, parent):        
        ttk.Button(
            parent, 
            text="色彩反转", 
            command=self.apply_reverse
        ).pack(fill=tk.X, pady=5)

    def create_rgb2gray_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="灰度化", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        # 第1行：红色边界
        ttk.Label(frame, text="红色R").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.rgb2gray_red_thresh = tk.IntVar(value=200)
        red_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.rgb2gray_red_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.rgb2gray_red_thresh_label, self.rgb2gray_red_thresh)
        )
        red_slider.grid(row=0, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.rgb2gray_red_thresh_label = ttk.Label(frame, text=str(self.rgb2gray_red_thresh.get()))
        self.rgb2gray_red_thresh_label.grid(row=0, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.rgb2gray_red_thresh_label, self.rgb2gray_red_thresh, 0)
        ).grid(row=0, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.rgb2gray_red_thresh_label, self.rgb2gray_red_thresh, 255)
        ).grid(row=0, column=4, padx=(5,0))

        # 第2行：绿色边界
        ttk.Label(frame, text="绿色G").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rgb2gray_green_thresh = tk.IntVar(value=50)
        green_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.rgb2gray_green_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.rgb2gray_green_thresh_label, self.rgb2gray_green_thresh)
        )
        green_slider.grid(row=1, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.rgb2gray_green_thresh_label = ttk.Label(frame, text=str(self.rgb2gray_green_thresh.get()))
        self.rgb2gray_green_thresh_label.grid(row=1, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.rgb2gray_green_thresh_label, self.rgb2gray_green_thresh, 0)
        ).grid(row=1, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.rgb2gray_green_thresh_label, self.rgb2gray_green_thresh, 255)
        ).grid(row=1, column=4, padx=(5,0))

        # 第3行：蓝色边界
        ttk.Label(frame, text="蓝色B").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.rgb2gray_blue_thresh = tk.IntVar(value=50)
        blue_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.rgb2gray_blue_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.rgb2gray_blue_thresh_label, self.rgb2gray_blue_thresh)
        )
        blue_slider.grid(row=2, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.rgb2gray_blue_thresh_label = ttk.Label(frame, text=str(self.rgb2gray_blue_thresh.get()))
        self.rgb2gray_blue_thresh_label.grid(row=2, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.rgb2gray_blue_thresh_label, self.rgb2gray_blue_thresh, 0)
        ).grid(row=2, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.rgb2gray_blue_thresh_label, self.rgb2gray_blue_thresh, 255)
        ).grid(row=2, column=4, padx=(5,0))
    
    def create_colorclean_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="净色", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # 配置列权重（所有行共用）
        frame.columnconfigure(0, weight=0)  # 标签
        frame.columnconfigure(1, weight=1)  # 滑块（可拉伸）
        frame.columnconfigure(2, weight=0)  # 数值标签
        frame.columnconfigure(3, weight=0)

        # 第1行：二值化边界
        ttk.Label(frame, text="二值边界").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.colorclean_binbonud_thresh = tk.IntVar(value=200)
        binbonud_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.colorclean_binbonud_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.colorclean_binbonud_thresh_label, self.colorclean_binbonud_thresh)
        )
        binbonud_slider.grid(row=0, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.colorclean_binbonud_thresh_label = ttk.Label(frame, text=str(self.colorclean_binbonud_thresh.get()))
        self.colorclean_binbonud_thresh_label.grid(row=0, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.colorclean_binbonud_thresh_label, self.colorclean_binbonud_thresh, 0)
        ).grid(row=0, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.colorclean_binbonud_thresh_label, self.colorclean_binbonud_thresh, 255)
        ).grid(row=0, column=4, padx=(5,0))

        # 第2行：红色起始
        ttk.Label(frame, text="红色起始").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.colorclean_redbound_thresh = tk.IntVar(value=50)
        redbound_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.colorclean_redbound_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.colorclean_redbound_thresh_label, self.colorclean_redbound_thresh)
        )
        redbound_slider.grid(row=1, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.colorclean_redbound_thresh_label = ttk.Label(frame, text=str(self.colorclean_redbound_thresh.get()))
        self.colorclean_redbound_thresh_label.grid(row=1, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.colorclean_redbound_thresh_label, self.colorclean_redbound_thresh, 0)
        ).grid(row=1, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.colorclean_redbound_thresh_label, self.colorclean_redbound_thresh, 255)
        ).grid(row=1, column=4, padx=(5,0))

        # 第3行：红色色差
        ttk.Label(frame, text="红色差距").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.colorclean_reddiff_thresh = tk.IntVar(value=50)
        reddiff_slider = ttk.Scale(
            frame, from_=0, to=255, variable=self.colorclean_reddiff_thresh,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_label(self.colorclean_reddiff_thresh_label, self.colorclean_reddiff_thresh)
        )
        reddiff_slider.grid(row=2, column=1, sticky=tk.EW, padx=(5,5), pady=2)
        self.colorclean_reddiff_thresh_label = ttk.Label(frame, text=str(self.colorclean_reddiff_thresh.get()))
        self.colorclean_reddiff_thresh_label.grid(row=2, column=2, padx=5)
        ttk.Button(
            frame, 
            text="-", 
            width=2,
            command=lambda: self.reduce_value(self.colorclean_reddiff_thresh_label, self.colorclean_reddiff_thresh, 0)
        ).grid(row=2, column=3, padx=(5,0))
        ttk.Button(
            frame, 
            text="+", 
            width=2,
            command=lambda: self.increment_value(self.colorclean_reddiff_thresh_label, self.colorclean_reddiff_thresh, 255)
        ).grid(row=2, column=4, padx=(5,0))
    
    def create_colormatrix(self, parent):
        # 创建一个 LabelFrame 作为分组容器
        frame = ttk.LabelFrame(parent, text="颜色矩阵", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.chart_type = tk.StringVar(value="颜色不变")
        
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

    def update_label(self, label_widget, intvar_widget):
        """更新滑块旁边的数值标签"""
        label_widget.config(text=str(intvar_widget.get()))

    def increment_value(self, label_widget, intvar, max_val=255):
        new_val = intvar.get() + 1
        if new_val <= max_val:
            intvar.set(new_val)
        label_widget.config(text=str(intvar.get()))

    def reduce_value(self, label_widget, intvar, min_val=0):
        # print(intvar.get(), end="")
        new_val = intvar.get() - 1
        if new_val >= min_val:
            # print(new_val, end="")
            intvar.set(new_val)
        # print(new_val, end="\n")
        label_widget.config(text=str(intvar.get()))

    def create_plot_area(self, parent):
        """创建图片显示区域（修改：增加固定尺寸和滚动条）"""
        control_frame = ttk.LabelFrame(parent, text="图片显示区域", padding=5)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="打开图片", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存结果", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行净色", command=self.apply_clean_color).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行灰度", command=self.apply_grayscale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行反转", command=self.apply_reverse).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行二值", command=self.apply_binarization).pack(side=tk.LEFT, padx=5)
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
    
    def load_image(self):
        """加载图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        
        try:
            # 打开并转为 RGB
            self.original_image = Image.open(file_path).convert("RGB")
            self.original_array = np.array(self.original_image)
            
            # 显示原图
            self.display_image(self.original_array, self.original_label, is_original=True)
            
            # 清空处理结果
            self.processed_array = None
            self.display_image(None, self.result_label, is_original=False)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片：{e}")
    
    def display_image(self, img_array, label_widget, is_original=True, max_width=800, max_height=800):
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
        bin_bound = self.colorclean_binbonud_thresh.get()   # 灰度二值化阈值
        red_start = self.colorclean_redbound_thresh.get()   # 红色通道最小值
        red_diff = self.colorclean_reddiff_thresh.get()     # R-G和R-B差值阈值
        
        result_array = self.process.document_clean(
            self.original_array,
            red_r_thresh=red_start,
            red_diff_thresh=red_diff,
            gray_thresh=bin_bound
        )
        
        self.processed_array = result_array
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
        # 也可以更新原图？看需求
    
    def apply_reverse(self):
        """反转颜色"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        reversed_img = self.process.reversed(self.original_array)
        self.processed_array = reversed_img
        self.display_image(self.processed_array, self.result_label, is_original=False)
    
    def apply_grayscale(self):
        """灰度化（使用当前RGB权重滑块）"""
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        r_w = self.rgb2gray_red_thresh.get() / 255.0   # 滑块值是整数0-255，转为权重
        g_w = self.rgb2gray_green_thresh.get() / 255.0
        b_w = self.rgb2gray_blue_thresh.get() / 255.0
        # 归一化权重和=1
        total = r_w + g_w + b_w
        if total != 0:
            r_w /= total
            g_w /= total
            b_w /= total
        self.processed_array = self.process.rgb2gray(self.original_array, weights=(r_w, g_w, b_w))
        # 灰度图转三通道（方便显示）
        gray_array = np.stack([self.processed_array, self.processed_array, self.processed_array], axis=2)
        self.display_image(gray_array, self.result_label, is_original=False)
    
    def apply_binarization(self):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return
        gray = self.binarization_gray_thresh.get()
        r_w = self.binarization_red_thresh.get() / 255.0   # 滑块值是整数0-255，转为权重
        g_w = self.binarization_green_thresh.get() / 255.0
        b_w = self.binarization_blue_thresh.get() / 255.0
        total = r_w + g_w + b_w
        if total != 0:
            r_w /= total
            g_w /= total
            b_w /= total
        self.processed_array = self.process.binarization(self.original_array, bound=gray, weights=(r_w, g_w, b_w))
        bina_array = np.stack([self.processed_array, self.processed_array, self.processed_array], axis=2)
        self.display_image(bina_array, self.result_label, is_original=False)
    
    def apply_color_matrix(self, matrix):
        if self.original_array is None:
            messagebox.showwarning("警告", "请先打开一张图片")
            return

        self.processed_array = self.process.color_matrix(self.original_array, matrix)
        self.display_image(self.processed_array, self.result_label, is_original=False)
        
    def save_result(self):
        """保存处理后的图片"""
        if self.processed_array is None:
            messagebox.showwarning("警告", "没有处理结果可保存")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPEG图片", "*.jpg"), ("所有文件", "*.*")]
        )
        if file_path:
            if self.processed_array.ndim == 2:
                Image.fromarray(self.processed_array, mode="L").save(file_path)
                messagebox.showinfo("成功保存为灰度图文件", f"图片已保存到：{file_path}")
            elif self.processed_array.ndim == 3:
                Image.fromarray(self.processed_array, mode="RGB").save(file_path)
                messagebox.showinfo("成功保存为彩色图文件", f"图片已保存到：{file_path}")
            else:
                messagebox.showinfo("保存错误", f"图片为保存")
if __name__ == "__main__":
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    app = PicPro(root)
    root.mainloop()