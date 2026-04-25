## file_name : image_process.py
import time
import numpy as np  # 用于生成测试图像和数组操作
from ctypes import CDLL, c_uint8, c_int, POINTER, Structure, c_float
from pathlib import Path
from typing import Union, Tuple, Dict
from PIL import Image

class RGBWeights(Structure):
    _fields_ = [
        ('r', c_float),
        ('g', c_float),
        ('b', c_float)
    ]

class ImageProcessor:
    """
    图像处理用的函数，在这个类里面，目前推荐的方法参考Methods

    Methods:
        rgb2gray():将RGB三通道图片数据转化为灰度图像数据
        gray2color():将灰度图像数据转换为伪彩色图像数据
        binarization():将灰度图像数据二值化
        rotate():旋转图像,灰度图和彩图都可以旋转
    Notes:
        - 调用"test_c\image_process.dll"的数据接口,仅提供基本操作
        - image_process.dll由gcc对image_process.c编译而来
        - 使用这个类，可以比Python的原生操作要快很多
        - 使用前，请确保数组在内存中连续，可以看参数img_data.flags['C_CONTIGUOUS']，用np.ascontiguousarray()使其连续
    Examples:
        >>> process = ImageProcessor()

        >>> pic_rgb = np.random.randint(0, 256, size=(1000, 1000, 3), dtype=np.uint8)

        >>> pic_gray = process.rgb_to_gray(pic_rgb)
    """
    def __init__(self):
        DLL_path = Path(__file__).parent / "image_process.dll" # .dll文件就在同级目录下
        self.lib = CDLL(str(DLL_path))
        self._init_types()

    def _init_types(self)-> None:
        """
        声明 C 函数的参数类型和返回值类型。
        
        这个方法用于初始化ctypes函数的参数类型，在类初始化时调用。
        """
        self.lib.rgb_to_gray.argtypes = [
            POINTER(c_uint8),  # rgb_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # gray_data（指针）
            RGBWeights         # weights
        ]
        self.lib.rgb_to_gray.restype = c_int

        self.lib.gray_set_color.argtypes = [
            POINTER(c_uint8), # gray_data（指针）
            c_int,
            c_int,
            POINTER(c_uint8), # rgb_data（指针）
            POINTER(c_uint8), # gray_to_idx
            POINTER(c_uint8), # red
            POINTER(c_uint8), # green
            POINTER(c_uint8), # blue
        ]
        self.lib.gray_set_color.restype = c_int

        self.lib.binarization.argtypes = [
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
            c_uint8
        ]
        self.lib.binarization.restype = c_int

        self.lib.gray_reversed.argtypes = [ #说是灰度反转，但是稍微操作一下就是彩图反转
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
        ]
        self.lib.gray_reversed.restype = c_int

        self.lib.rotate_gray_90_cw.argtypes = [
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
        ]
        self.lib.rotate_gray_90_cw.restype = c_int

        self.lib.rotate_gray_90_ccw.argtypes = [
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
        ]
        self.lib.rotate_gray_90_ccw.restype = c_int

        self.lib.rotate_rgb_90_cw.argtypes = [
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
        ]
        self.lib.rotate_rgb_90_cw.restype = c_int

        self.lib.rotate_rgb_90_ccw.argtypes = [
            POINTER(c_uint8),  # gray_data（指针）
            c_int,             # width
            c_int,             # height
            POINTER(c_uint8),   # return_gray_data（指针）
        ]
        self.lib.rotate_rgb_90_ccw.restype = c_int

        # 文档清理函数
        self.lib.clean_document.argtypes = [
            POINTER(c_uint8),  # src_rgb
            c_int,             # height
            c_int,             # width
            POINTER(c_uint8),  # dst_rgb
            c_int,             # red_r_thresh
            c_int,             # red_diff_thresh
            c_int              # gray_thresh
        ]
        self.lib.clean_document.restype = c_int

        # const uint8_t* src_rgb, int height, int width, uint8_t* dst_rgb, const float color_matrix[9]
        self.lib.color_matrix.argtypes = [
            POINTER(c_uint8),
            c_int,
            c_int,
            POINTER(c_uint8),
            POINTER(c_float)
        ]
        self.lib.color_matrix.restype = c_int

        # int convolution_gray_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge)
        self.lib.convolution_gray_std.argtypes = [
            POINTER(c_uint8),
            c_int,
            c_int,
            POINTER(c_uint8),
            POINTER(c_float),
            c_int
        ]
        self.lib.convolution_gray_std.restype = c_int

        # int convolution_rgb_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge)
        self.lib.convolution_rgb_std.argtypes = [
            POINTER(c_uint8),
            c_int,
            c_int,
            POINTER(c_uint8),
            POINTER(c_float),
            c_int
        ]
        self.lib.convolution_rgb_std.restype = c_int
    ### 直接的接口函数
    def rgb2gray(self, rgb_data: np.ndarray, weights:Tuple = (0.299, 0.587, 0.114)) -> np.ndarray:
        """
        将RGB三通道图片数据转化为灰度图像数据

        Args:
            rgb_data : 输入图像（numpy 数组，shape 为 (height, width, 3)，dtype=uint8）
            weights : rgb权重元组
        
        Returns:
            gray_data : 灰度图像（numpy 数组，shape 为 (height, width)，dtype=uint8）
        """
        height, width, _ = rgb_data.shape

        rgb_ptr = rgb_data.ctypes.data_as(POINTER(c_uint8)) 

        gray_data = np.zeros((height, width), dtype=np.uint8)
        gray_ptr = gray_data.ctypes.data_as(POINTER(c_uint8))

        weight_struct = RGBWeights(r=weights[0], g=weights[1], b=weights[2]) # 把权重处理为结构体

        result = self.lib.rgb_to_gray(rgb_ptr, height, width, gray_ptr, weight_struct)

        if result != 0:
            raise ValueError("C函数执行失败，错误码: {}".format(result))
        
        return gray_data
    
    def gray2color(self, gray_data: np.ndarray, color_map: Union[Dict[int, Tuple[int, int, int]], Dict[int, str]]) -> np.ndarray:
        """
        将灰度图像数据转换为伪彩色图像数据

        Args:
            gray_data: 输入灰度图像（numpy 数组，shape 为 (height, width)，dtype=uint8）
            color_map: 颜色映射表，灰度值:(R, G, B) 或者 灰度值:HEX
            
        Returns:
            伪彩色RGB图像 shape = (H, W, 3)
        """
        height, width = gray_data.shape

        first_value = next(iter(color_map.values())) # 第一个键值对的值
        if isinstance(first_value, tuple) and len(first_value)== 3 and all(isinstance(x, int) for x in first_value):
            gray_arr, red_arr, green_arr, blue_arr = self.create_color_list_from_dict(color_map)
        elif isinstance(first_value, str):
            color_map_ = {}
            for gray, string in color_map.items():
                hex_color = string.lstrip('#')
                if len(hex_color) != 6:
                    raise ValueError(f"颜色字符串必须是6位十六进制数，得到: {hex_color}")
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color_map_[gray] = (r, g, b)
            gray_arr, red_arr, green_arr, blue_arr = self.create_color_list_from_dict(color_map_)
        else:
            raise ValueError("不支持的颜色映射表类型")
        
        gray_to_idx = np.zeros(256, dtype=np.uint8) # 256个数字的转换表
        for idx, gray in enumerate(gray_arr):
            gray_to_idx[gray] = idx

        rgb_data = np.zeros((height, width, 3), dtype=np.uint8)
        
        gray_ptr = gray_data.ctypes.data_as(POINTER(c_uint8))
        rgb_ptr = rgb_data.ctypes.data_as(POINTER(c_uint8))
        gray_idx_ptr = gray_to_idx.ctypes.data_as(POINTER(c_uint8))
        red_ptr = red_arr.ctypes.data_as(POINTER(c_uint8))
        green_ptr = green_arr.ctypes.data_as(POINTER(c_uint8))
        blue_ptr = blue_arr.ctypes.data_as(POINTER(c_uint8))
        
        result = self.lib.gray_set_color(gray_ptr, width, height, rgb_ptr,
                                        gray_idx_ptr, red_ptr, green_ptr, blue_ptr)
        
        if result != 0:
            raise RuntimeError("gray_set_color C函数执行失败")
        
        return rgb_data
    
    def gray_binarization(self, gray_data:np.ndarray, bound:int)->np.ndarray:
        """
        将灰度图像数据二值化

        Args:
            gray_data : 输入灰度图像（numpy 数组，shape 为 (height, width)，dtype=uint8）
            bound : 边界值，大于该边界值变为255，小于或等于该边界值变为0
        
        Returns:
            return_gray_data : 灰度图像（numpy 数组，shape 为 (height, width)，dtype=uint8）
        """
        height, width = gray_data.shape

        return_gray_data = np.zeros((height, width), dtype=np.uint8)

        gray_data_ptr = gray_data.ctypes.data_as(POINTER(c_uint8))
        return_gray_data_ptr = return_gray_data.ctypes.data_as(POINTER(c_uint8))

        result = self.lib.binarization(gray_data_ptr, height, width, return_gray_data_ptr, bound)

        if result != 0:
            raise RuntimeError("binarization C函数执行失败")
        return return_gray_data
    
    def binarization(self, img_data:np.ndarray, bound:int, weights:Tuple =(0.299, 0.587, 0.114))->np.ndarray:
        """
        将图像数据二值化

        Args:
            img_data : 输入图像, RGB图(H,W,3) or 灰度图(H,W), (np.ndarray, np.uint8)
            bound : 边界值，大于该边界值变为255，小于或等于该边界值变为0
            reversed : 是否反转，不反转就是亮的地方亮
            weights : 灰度图的操作不需要这个,默认值为(0.299, 0.587, 0.114)
        Returns:
            return_gray_data : 灰度图像（numpy 数组，shape 为 (height, width)，dtype=uint8）
        """
        # print(weights)
        if img_data.ndim not in [2, 3]:
            raise ValueError(f"不支持的数组维度: {img_data.ndim}，必须是2(灰度)或3(RGB)")
        
        if img_data.ndim == 3 and img_data.shape[2] != 3:
            raise ValueError(f"RGB图像必须形状为(H,W,3)，得到: {img_data.shape}")
        
        if img_data.ndim == 2:
            pic = self.gray_binarization(img_data, bound)
        else:
            gray_data = self.rgb2gray(img_data, weights)
            pic = self.gray_binarization(gray_data, bound)
        
        return pic

    def _rotate_90_gray(self, image_array: np.ndarray, clockwise: bool = True) -> np.ndarray:
        """
        旋转图像90度（支持灰度和RGB图像）
        
        Args:
            image_array: 输入图像数组，灰度图(H,W)
            clockwise: 是否顺时针旋转
            
        Returns:
            旋转后的图像数组
            
        Raises:
            ValueError: 如果输入数组形状不支持
        """
        height, width = image_array.shape
        
        dst_height, dst_width = width, height  # 旋转后宽高互换
        rotated = np.zeros((dst_height, dst_width), dtype=np.uint8)
        
        # 选择函数
        if clockwise:
            func = self.lib.rotate_gray_90_cw
        else:
            func = self.lib.rotate_gray_90_ccw
        
        # 获取指针
        src_ptr = image_array.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = rotated.ctypes.data_as(POINTER(c_uint8))
        
        # 调用C函数
        result = func(src_ptr, height, width, dst_ptr)
        
        if result != 0:
            raise RuntimeError(f"旋转失败，错误码: {result}")
        
        return rotated
    
    def _rotate_90_rgb(self, image_array: np.ndarray, clockwise: bool = True) -> np.ndarray:
        """
        旋转图像90度（支持灰度和RGB图像）
        
        Args:
            image_array: 输入图像数组，RGB图(H,W,3)
            clockwise: 是否顺时针旋转
            
        Returns:
            旋转后的图像数组
            
        Raises:
            ValueError: 如果输入数组形状不支持
        """
        height, width, _ = image_array.shape

        # RGB图
        dst_height, dst_width = width, height
        
        # 创建输出数组
        rotated = np.zeros((dst_height, dst_width, 3), dtype=np.uint8)
        
        # 选择函数
        if clockwise:
            func = self.lib.rotate_rgb_90_cw
        else:
            func = self.lib.rotate_rgb_90_ccw
        
        # 获取指针
        src_ptr = image_array.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = rotated.ctypes.data_as(POINTER(c_uint8))
        
        # 调用C函数
        result = func(src_ptr, height, width, dst_ptr)
        
        if result != 0:
            raise RuntimeError(f"旋转失败，错误码: {result}")
        
        return rotated
    
    def rotate_90(self, image_array: np.ndarray, clockwise: bool = True) -> np.ndarray:
        if image_array.ndim not in [2, 3]:
            raise ValueError(f"不支持的数组维度: {image_array.ndim}，必须是2(灰度)或3(RGB)")
        
        if image_array.ndim == 3 and image_array.shape[2] != 3:
            raise ValueError(f"RGB图像必须形状为(H,W,3)，得到: {image_array.shape}")
        
        if image_array.ndim == 2:
            rotated = self._rotate_90_gray(image_array, clockwise)
        else:
            rotated = self._rotate_90_rgb(image_array, clockwise)
        
        return rotated
    
    def reversed(self, img_data:np.ndarray)->np.ndarray:
        """
        将图像数据反转(i->255-i)

        Args:
            img_data : 输入图像，RGB图(H,W,3) or 灰度图(H,W), (np.ndarray, np.uint8)
        
        Returns:
            reversed_img : 输出图像，RGB图(H,W,3) or 灰度图(H,W), (np.ndarray, np.uint8)
        """
        if img_data.ndim not in [2, 3]:
            raise ValueError(f"不支持的数组维度: {img_data.ndim}，必须是2(灰度)或3(RGB)")
        
        if img_data.ndim == 3 and img_data.shape[2] != 3:
            raise ValueError(f"RGB图像必须形状为(H,W,3)，得到: {img_data.shape}")
        
        if img_data.ndim == 2:
            height, width = img_data.shape
            reversed_img = np.zeros((height, width), dtype=np.uint8)
        else:
            height, width, _ = img_data.shape
            reversed_img = np.zeros((height, width,3), dtype=np.uint8)
            height = height*3 # 这里是关键，因为反向操作直接到了每一个像元的每一个通道，所以只需要让height*width等于所要改变的数据个数就行了
        
        gray_data_ptr = img_data.ctypes.data_as(POINTER(c_uint8))
        return_gray_data_ptr = reversed_img.ctypes.data_as(POINTER(c_uint8))

        result = self.lib.gray_reversed(gray_data_ptr, height, width, return_gray_data_ptr)

        if result != 0:
            raise RuntimeError("binary_reversed C函数执行失败")
        return reversed_img
    
    def rotate(self, image_array: np.ndarray, angle: int = 90) -> np.ndarray:
        """
        这个方法以后使用形变矩阵实现，注意，当前未实现该方法！！！
        顺时针旋转图像（支持90、180、270度）
        
        Args:
            image_array: 输入图像,RGB图(H,W,3)或灰度图(H,W), np.ndarray, np.uint8
            angle: 顺时针旋转角度，必须是90的倍数
            
        Returns:
            旋转后的图像数组
        """
        pass

    def document_clean(self, rgb_image: np.ndarray,
                   red_r_thresh: int = 200,
                   red_diff_thresh: int = 50,
                   gray_thresh: int = 128) -> np.ndarray:
        """
        将手机拍摄的文档（白底黑字红章）处理成纯白、纯黑、纯红三色图。
        
        Args:
            rgb_image: 输入RGB图像 (H, W, 3), dtype=uint8
            red_r_thresh: 红色通道最小值，默认200
            red_diff_thresh: R与G/B的最小差值，默认50
            gray_thresh: 黑白二值化阈值（0~255），auto_threshold=False时使用
            auto_threshold: 是否自动计算黑白阈值（Otsu），默认True
        
        Returns:
            三值化后的RGB图像 (H, W, 3)
        """
        if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
            raise ValueError("输入必须是RGB图像 (H, W, 3)")
        
        height, width, _ = rgb_image.shape
        dst_rgb = np.zeros((height, width, 3), dtype=np.uint8)
        
        src_ptr = rgb_image.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = dst_rgb.ctypes.data_as(POINTER(c_uint8))
        

        result = self.lib.clean_document(src_ptr, height, width, dst_ptr,
                                            red_r_thresh, red_diff_thresh, gray_thresh)
        
        if result != 0:
            raise RuntimeError(f"document_clean 执行失败，错误码: {result}")
        
        return dst_rgb
    
    def color_matrix(self, rgb_image:np.ndarray, color_matrix:list[list[float]]) -> np.ndarray:
        if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
            raise ValueError("输入必须是RGB图像 (H, W, 3)")
        
        height, width, _ = rgb_image.shape
        dst_rgb = np.zeros((height, width, 3), dtype=np.uint8)

        src_ptr = rgb_image.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = dst_rgb.ctypes.data_as(POINTER(c_uint8))
        flat_matrix = [x for row in color_matrix for x in row]
        mat_ptr = (c_float * 9)(*flat_matrix)

        result = self.lib.color_matrix(src_ptr, height, width, dst_ptr, mat_ptr)

        if result != 0:
            raise RuntimeError(f"document_clean 执行失败，错误码: {result}")
        
        return dst_rgb
    
    # int convolution_gray_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge)
    def _convolution_gray_std(self, gray_image:np.ndarray, kernel:np.ndarray):
        """
        灰度图卷积操作

        Args:
            gray_image : 输入图像，灰度图(H,W), (np.ndarray, np.uint8)
            kernel : 卷积核, 正方形, (np.ndarray, np.float)
        
        Returns:
            conv_image : 输出图像，灰度图(H,W), (np.ndarray, np.uint8)
        """        
        height, width = gray_image.shape
        dst = np.zeros((height, width), dtype=np.uint8)

        src_ptr = gray_image.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = dst.ctypes.data_as(POINTER(c_uint8))
        kernel_ptr = kernel.ctypes.data_as(POINTER(c_float))
        kernel_edge = kernel.shape[0]

        result = self.lib.convolution_gray_std(src_ptr, height, width, dst_ptr, kernel_ptr, kernel_edge)

        if result != 0:
            raise RuntimeError(f"convolution_gray_std 执行失败，错误码: {result}")
        
        return dst
    
    # int convolution_rgb_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge)
    def _convolution_rgb_std(self, rgb_image:np.ndarray, kernel:np.ndarray):
        """
        rgb彩图卷积操作

        Args:
            rgb_image: 输入RGB图像 (H, W, 3), dtype=uint8
            kernel : 卷积核, 正方形, (np.ndarray, np.float)
        
        Returns:
            conv_image : 输出RGB图像 (H, W, 3), dtype=uint8
        """
        height, width, _ = rgb_image.shape
        dst = np.zeros((height, width, 3), dtype=np.uint8)

        src_ptr = rgb_image.ctypes.data_as(POINTER(c_uint8))
        dst_ptr = dst.ctypes.data_as(POINTER(c_uint8))
        kernel_ptr = kernel.ctypes.data_as(POINTER(c_float))
        kernel_edge = kernel.shape[0]

        result = self.lib.convolution_rgb_std(src_ptr, height, width, dst_ptr, kernel_ptr, kernel_edge)

        if result != 0:
            raise RuntimeError(f"convolution_rgb_std 执行失败，错误码: {result}")
        
        return dst
    
    def convolution_std(self, image_array: np.ndarray, kernel:list[list[float]]):
        """
        图像卷积操作

        Args:
            image_array: 输入图像,RGB图(H,W,3)或灰度图(H,W), np.ndarray, np.uint8
            kernel : 卷积核, 正方形, (np.ndarray, np.float)
        
        Returns:
            conv_image : 输出图像,RGB图(H,W,3)或灰度图(H,W), np.ndarray, np.uint8
        """
        k_np = np.asarray(kernel, dtype=np.float32)
        if image_array.ndim not in [2, 3]:
            raise ValueError(f"不支持的数组维度: {image_array.ndim}，必须是2(灰度)或3(RGB)")
        if k_np.shape[0] % 2 == 0:
            raise ValueError("kernel edge must be odd")
        
        if image_array.ndim == 2:
            dst = self._convolution_gray_std(image_array, k_np)
        else:
            dst = self._convolution_rgb_std(image_array, k_np)
        
        return dst
    
    ### 辅助函数
    def create_color_list_from_dict(self, color_map: Dict[int, Tuple[int, int, int]])->Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        被类方法self.gray_to_color调用,从字典创建颜色映射表

        Args:
            color_map: 用字典表示的颜色映射表，形式为---灰度值:(R, G, B)

        Returns:
            (gray_arr, red_arr, green_arr, blue_arr) : 数据格式均为np.uint8
        """
        sorted_items = sorted(color_map.items())
            
        gray_arr = np.array([gray for gray, _ in sorted_items], dtype=np.uint8)
        color_arr = np.array([color for _, color in sorted_items], dtype=np.uint8) # 其实可以优化，直接把这个给C函数
        
        red_arr = color_arr[:, 0].copy()
        green_arr = color_arr[:, 1].copy() 
        blue_arr = color_arr[:, 2].copy()

        return gray_arr, red_arr, green_arr, blue_arr

# 代码运行时间装饰器
def ProcessTime(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        total_time = time.time() - start
        print(f"处理耗时：{total_time:.4f} 秒")
        return result
    return inner

# 测试性能
if __name__ == "__main__":
    # 生成一张 4000x3000 的随机 RGB 图像（约 36MB）
    height, width = 3000, 4000
    rgb_image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

    processor = ImageProcessor()
    start = time.time()
    c_gray = processor.rgb2gray(rgb_image)
    c_time = time.time() - start
    print(f"C 实现耗时：{c_time:.4f} 秒")