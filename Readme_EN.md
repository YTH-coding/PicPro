# PicPro - Image Processing Tool

A desktop image processing tool with a graphical interface that uses Python to call C libraries for high-performance image manipulation. Core computations are handled via `ctypes` binding to a C-compiled DLL.

## Features

- **Basic Operations**: Open/save images (color/grayscale), create custom images
- **Rotation**: 90° clockwise/counterclockwise rotation
- **Color Inversion**: Invert image colors
- **Grayscale**: Convert color images to grayscale with customizable RGB weights
- **Binarization**: Black-and-white thresholding with adjustable threshold and RGB weights
- **Pseudo-color**: Map grayscale images to custom colors with color presets
- **Document Clean**: Process scanned/photographed documents (white background, black text, red seal) into pure white, black, and red three-color output
- **Color Matrix**: Apply 3x3 color matrices for various filter effects (vintage, cool tone, high contrast, etc.)
- **Convolution**: Blur, sharpen, edge detection, emboss, and other convolution-based effects
- **New Image**: Create custom-sized images with pixel values distributed by probability

## Requirements

- **OS**: Windows 10 / Windows 11 (other OSes untested)
- **Python**: 3.10 ~ 3.14 (developed with 3.11)
- **GCC**: Required to compile the C source code into a DLL
- **Dependencies**:
  - `numpy` — Image data storage and transfer
  - `Pillow` — Image file I/O

## Installation & Usage

### 1. Install Python dependencies

```bash
pip install numpy pillow
```

### 2. Compile the C shared library

```bash
gcc -O3 -shared -o core/image_process.dll core/image_process.c
```

### 3. Run the application

```bash
python main.py
```

## Project Structure

```
PicPro/
├── main.py                        # GUI main program (tkinter)
├── color.py                       # Pseudo-color mapping dialog
├── newpic.py                      # New image creation dialog
│
├── core/
│   ├── image_process.c            # C image processing core source
│   ├── image_process.dll          # Compiled shared library
│   └── image_process.py           # Python wrapper (ctypes bindings)
│
├── config/
│   ├── color_matrix.json          # Color matrix filter presets (16 filters)
│   ├── color_preset.json          # Named color presets (32 colors)
│   └── convolution.py             # Convolution kernel definitions
│
├── test/                          # Test scripts
├── .vscode/                       # VS Code configuration
├── LICENSE                        # MIT License
└── Readme_EN.md                   # English documentation (this file)
```

## Architecture

```
main.py ──→ ImageProcessor (ctypes) ──→ image_process.dll (C compiled)
    │
    ├── color.py        ──→ Pseudo-color mapping
    ├── newpic.py       ──→ New image creation
    ├── config/
    │   ├── color_matrix.json  ──→ Filter parameters
    │   ├── color_preset.json  ──→ Color presets
    │   └── convolution.py     ──→ Convolution kernels
    └── core/
        └── image_process.py  ──→ C function wrapper
```

Python calls the C-compiled DLL via `ctypes`, leveraging C's high performance for processing large image data.

## License

This project is open-sourced under the MIT License. See [LICENSE](LICENSE) for details.
