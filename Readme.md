# PicPro - 图像处理工具

一个使用 Python 调用 C 语言编写的图像处理桌面工具，集成图形界面，支持多种图像处理功能。核心运算通过 `ctypes` 调用 C 编译的 DLL 实现高性能处理。

## 功能

- **基本操作**：打开/保存图片（彩图/灰度图）、新建自定义图片
- **旋转变换**：顺时针/逆时针 90° 旋转
- **色彩反转**：反转图像颜色
- **灰度化**：自定义 RGB 权重将彩色图转为灰度图
- **二值化**：可调阈值和 RGB 权重的黑白二值化
- **伪彩色化**：将灰度图映射为自定义彩色图，支持颜色预设
- **文档净色**：将扫描/拍摄的文档（白底黑字红章）处理为纯白、纯黑、纯红三色图
- **颜色矩阵**：通过 3x3 颜色矩阵实现多种滤镜效果（复古、冷色调、高对比等）
- **卷积操作**：支持模糊、锐化、边缘检测、浮雕等效果
- **新建图片**：自定义尺寸，按概率分布生成像素图案

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
gcc -O3 -shared -o core/image_process.dll core/image_process.c
```

### 3. 运行程序

```bash
python main.py
```

## 项目结构

```
PicPro/
├── main.py                        # GUI 主程序（tkinter）
├── color.py                       # 伪彩色映射配置对话框
├── newpic.py                      # 新建图片对话框
│
├── core/
│   ├── image_process.c            # C 语言图像处理核心源码
│   ├── image_process.dll          # 编译后的动态库
│   └── image_process.py           # Python 封装层（ctypes 调用 DLL）
│
├── config/
│   ├── color_matrix.json          # 颜色矩阵滤镜预设（16 种）
│   ├── color_preset.json          # 颜色名称预设（32 种中西色彩）
│   └── convolution.py             # 卷积核定义（模糊/锐化/边缘检测/特效）
│
├── test/                          # 测试脚本
├── .vscode/                       # VS Code 配置
├── LICENSE                        # MIT 许可证
└── Readme.md                      # 本文件
```

## 技术架构

```
main.py ──→ ImageProcessor (ctypes) ──→ image_process.dll (C 编译)
    │
    ├── color.py        ──→ 伪彩色映射
    ├── newpic.py       ──→ 新建图片
    ├── config/
    │   ├── color_matrix.json  ──→ 滤镜参数
    │   ├── color_preset.json  ──→ 颜色预设
    │   └── convolution.py     ──→ 卷积核
    └── core/
        └── image_process.py  ──→ C 函数封装
```

Python 通过 `ctypes` 调用 C 语言编译的 DLL，利用 C 的高性能处理大规模图像数据。

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE)。
