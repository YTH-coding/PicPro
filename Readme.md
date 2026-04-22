# PicPro - 图像处理工具

一个使用 Python 调用 C 语言编写的图像处理桌面工具，支持多种图像处理功能。

## 功能

- **灰度化**：自定义 RGB 权重将彩色图转为灰度图
- **二值化**：可调阈值和 RGB 权重的黑白二值化
- **色彩反转**：反转图像颜色
- **旋转**：顺时针/逆时针 90 度旋转
- **文档净色**：将扫描/拍摄的文档（白底黑字红章）处理为纯白、纯黑、纯红三色图
- **颜色矩阵变换**：通过 3x3 颜色矩阵实现色调调整（配置在 `config/color_matrix.json`）

## 环境要求

- **操作系统**：Windows 10 / Windows 11（其他系统未测试）
- **Python**：3.10 ~ 3.14（开发使用 3.11）
- **GCC**：用于将 C 源码编译为 DLL
- **依赖库**：
  - `numpy` —— 图像数据存储与传递
  - `Pillow` —— 图片文件的读写

## 安装与使用

### 1. 安装 Python 依赖

```bash
pip install numpy pillow
```

### 2. 编译 C 动态库

```bash
gcc -O3 -shared -o test_c/image_process.dll test_c/image_process.c
```

### 3. 运行程序

```bash
python main.py
```

## 项目结构

```
PicPro/
├── main.py                   # GUI 主程序（tkinter）
├── config/
│   └── color_matrix.json     # 颜色矩阵预设
├── test_c/
│   ├── image_process.c       # C 语言图像处理核心
│   ├── image_process.dll     # 编译后的动态库
│   └── image_process.py      # Python 封装层（ctypes 调用 DLL）
├── LICENSE                   # MIT 许可证
└── Readme.md                 # 本文件
```

## 技术架构

```
main.py → ImageProcessor (Python 封装) → ctypes → image_process.dll (C 编译)
```

Python 通过 `ctypes` 调用 C 语言编译的 DLL，利用 C 的高性能处理大规模图像数据。

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE)。
