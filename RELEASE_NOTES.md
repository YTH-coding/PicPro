# PicPro v1.0.0 — 图像处理工具 / Image Processing Tool

> 一个使用 Python 调用 C 语言编写的图像处理桌面工具。
> A desktop image processing tool that combines Python's ease of use with C's performance via ctypes.

[中文](#中文) | [English](#english)

---

## 中文

### 概述

PicPro 是一个基于 tkinter 的桌面图像处理工具，核心运算通过 `ctypes` 调用 C 编译的 DLL 实现高性能处理。提供了从基础操作到高级滤波的完整图像处理管线。

### 功能特性

- **文件操作**：打开/保存彩图与灰度图，支持 JPEG/PNG/BMP/TIFF
- **新建图片**：自定义尺寸，按概率分布生成像素图案
- **旋转变换**：顺时针/逆时针 90° 旋转
- **色彩反转**：一键反转图像颜色
- **灰度化**：自定义 RGB 权重（滑块实时调节）
- **二值化**：可调阈值及 RGB 权重
- **伪彩色化**：灰度图映射为彩色，支持 32 种中西颜色预设，支持 HEX/RGB 输入与随机映射
- **文档净色**：将扫描件/拍摄文档处理为纯白、纯黑、纯红三色图，适合文档去背景
- **颜色矩阵滤镜**：内置 16 种滤镜（复古、冷色调、高对比、胶片感等），可扩展
- **卷积操作**：支持均值模糊、高斯模糊、锐化、边缘检测（Sobel/Laplacian/Prewitt）、浮雕等 13 种卷积核

### 技术栈

| 层次 | 技术 |
|------|------|
| GUI 框架 | Python tkinter / ttk |
| 图像处理后端 | C 语言（编译为 DLL） |
| Python-C 互调 | ctypes |
| 数据处理 | numpy + Pillow |

### 快速开始

```bash
pip install numpy pillow
gcc -O3 -shared -o core/image_process.dll core/image_process.c
python main.py
```

### 项目结构

```
PicPro/
├── main.py                        # GUI 主程序
├── sub_ui/                        # 功能弹窗
│   ├── color.py                   # 伪彩色映射对话框
│   └── newpic.py                  # 新建图片对话框
├── core/
│   ├── image_process.c            # C 核心源码
│   ├── image_process.dll          # 编译后的动态库
│   └── image_process.py           # Python ctypes 封装
├── config/
│   ├── color_matrix.json          # 16 种矩阵滤镜
│   ├── color_preset.json          # 32 种颜色预设
│   └── convolution.py             # 13 种卷积核
└── LICENSE                        # MIT
```

---

## English

### Overview

PicPro is a tkinter-based GUI application that calls C-compiled DLLs through `ctypes` for high-performance pixel operations. It provides a complete image processing pipeline from basic transforms to advanced convolution filters.

### Features

- **File I/O**: Open and save color / grayscale images (JPEG, PNG, BMP, TIFF)
- **New Image**: Generate custom-sized images with probability-based pixel distribution
- **Rotation**: 90° clockwise / counterclockwise
- **Color Inversion**: Invert all channels with one click
- **Grayscale**: Real-time adjustable RGB weights via sliders
- **Binarization**: Adjustable threshold and RGB weights
- **Pseudo-color**: Map grayscale values to custom colors — 32 built-in color presets (Chinese & Western), HEX/RGB input, and random mapping
- **Document Clean**: Process scanned documents into pure white / black / red three-color output — ideal for document background removal
- **Color Matrix Filter**: 16 built-in presets (vintage, cool tone, high contrast, film-like, etc.) — easily extensible via JSON
- **Convolution**: 13 kernels — mean blur, Gaussian blur, sharpening, edge detection (Sobel / Laplacian / Prewitt), emboss, and more

### Tech Stack

| Layer | Technology |
|-------|-----------|
| GUI | Python tkinter / ttk |
| Processing Engine | C (compiled to DLL) |
| Python-C Bridge | ctypes |
| Data | numpy + Pillow |

### Quick Start

```bash
pip install numpy pillow
gcc -O3 -shared -o core/image_process.dll core/image_process.c
python main.py
```

### Project Layout

```
PicPro/
├── main.py                        # GUI entry point
├── sub_ui/                        # Dialog windows
│   ├── color.py                   # Pseudo-color mapping dialog
│   └── newpic.py                  # New image dialog
├── core/
│   ├── image_process.c            # C source code
│   ├── image_process.dll          # Compiled binary
│   └── image_process.py           # Python ctypes wrapper
├── config/
│   ├── color_matrix.json          # 16 matrix filters
│   ├── color_preset.json          # 32 color presets
│   └── convolution.py             # 13 convolution kernels
└── LICENSE                        # MIT
```

### Requirements

- **OS**: Windows 10 / 11 (others untested)
- **Python**: 3.10–3.14 (developed with 3.11)
- **GCC**: to compile the C source into DLL
- **Dependencies**: `numpy`, `Pillow`

---

**License**: MIT
