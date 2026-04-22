# PicPro - Image Processing Tool

A desktop image processing tool that uses Python to call C libraries for high-performance image manipulation.

## Features

- **Grayscale**: Convert color images to grayscale with customizable RGB weights
- **Binarization**: Black-and-white thresholding with adjustable RGB weights
- **Color Inversion**: Invert image colors
- **Rotation**: 90-degree clockwise/counterclockwise rotation
- **Document Clean**: Process scanned/photographed documents (white background, black text, red seal) into pure white, black, and red three-color output
- **Color Matrix**: Apply 3x3 color matrices for tone adjustment (configured in `config/color_matrix.json`)

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
gcc -O3 -shared -o test_c/image_process.dll test_c/image_process.c
```

### 3. Run the application

```bash
python main.py
```

## Project Structure

```
PicPro/
├── main.py                   # GUI main program (tkinter)
├── config/
│   └── color_matrix.json     # Color matrix presets
├── test_c/
│   ├── image_process.c       # C image processing core
│   ├── image_process.dll     # Compiled shared library
│   └── image_process.py      # Python wrapper (ctypes bindings)
├── LICENSE                   # MIT License
├── Readme.md                 # Chinese documentation
└── Readme_EN.md              # English documentation (this file)
```

## Architecture

```
main.py → ImageProcessor (Python wrapper) → ctypes → image_process.dll (C compiled)
```

Python calls the C-compiled DLL via `ctypes`, leveraging C's high performance for processing large image data.

## License

This project is open-sourced under the MIT License. See [LICENSE](LICENSE) for details.
