from test_c.image_process import ImageProcessor
import numpy as np
from PIL import Image
import time

def bigger(mask: np.ndarray, size: int):
    return np.repeat(np.repeat(mask, size, axis=0), size, axis=1)

size = 5

shape = np.array([80,80])

a = np.zeros(shape*size, dtype=np.uint8)

po1 = (np.random.random(shape) < 0.15)
a[bigger(po1, size)] = 8

po1 = (np.random.random(shape) < 0.15)
a[bigger(po1, size)] = 16

po1 = (np.random.random(shape) < 0.15)
a[bigger(po1, size)] = 32

# 推荐使用该方式定义颜色
color = {
    0:"#FFFFFF",
    8:"#9846FD",
    16:"#91FFF8",
    32:"#FF7337",
}

process = ImageProcessor()

print("开始处理信息")
start = time.time()
rgb = process.gray2color(a, color)
all_time = time.time() - start
print("信息处理结束")
print(f"处理耗时:{all_time:^.8f}秒")

img = Image.fromarray(rgb, mode="RGB") # 保存图片
img.save("output.png", format="png")
