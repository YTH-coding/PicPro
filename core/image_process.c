//file_name : image_process.c
//编译命令为 : gcc -O3 -shared -o core/image_process.dll core/image_process.c

#include <stdint.h>  // 使用uint8_t

// 定义权重结构体
typedef struct {
    float r;
    float g;
    float b;
} RGBWeights;

int rgb_to_gray(const uint8_t* rgb_data, int height, int width, uint8_t* gray_data, RGBWeights weights) {
    if (rgb_data == NULL || gray_data == NULL || width <= 0 || height <= 0) {
        return -1;
    }

    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; i++) {
        const int idx = i * 3;
        float gray_f = 
            rgb_data[idx] * weights.r +
            rgb_data[idx + 1] * weights.g +
            rgb_data[idx + 2] * weights.b;
        
        // 饱和并转换为 uint8_t
        int gray_int = (int)(gray_f + 0.5f);  // 四舍五入
        if (gray_int < 0) gray_int = 0;
        if (gray_int > 255) gray_int = 255;
        gray_data[i] = (uint8_t)gray_int;
    }
    return 0;
}

int gray_set_color(const uint8_t* gray_data, int width, int height, 
    uint8_t* rgb_data, uint8_t* gray_to_idx, 
    const uint8_t* red_num, const uint8_t* green_num, const uint8_t* blue_num ){
    if (rgb_data == NULL || gray_data == NULL || width <= 0 || height <= 0 ||
        gray_to_idx == NULL || red_num == NULL || green_num == NULL || blue_num == NULL) {
        return -1;
    }

    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; i++){
        uint8_t color = gray_data[i];
        uint8_t idx = gray_to_idx[color];
        const int idx_rgb = i * 3;
        rgb_data[idx_rgb] = red_num[idx];
        rgb_data[idx_rgb+1] = green_num[idx];
        rgb_data[idx_rgb+2] = blue_num[idx];
    }
    return 0;
}

int binarization(const uint8_t* gray_data, int width, int height, uint8_t* return_gray_data, int bound) {
    if (gray_data == NULL || gray_data == NULL || width <= 0 || height <= 0) {
        return -1; // 或返回错误码
    }

    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; i++) {
        return_gray_data[i] = (gray_data[i] > bound ? 255 : 0 );
    }
    return 0;
}

int binarization_reversed(const uint8_t* gray_data, int width, int height, uint8_t* return_gray_data, int bound) {
    if (gray_data == NULL || gray_data == NULL || width <= 0 || height <= 0) {
        return -1; // 或返回错误码
    }

    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; i++) {
        return_gray_data[i] = (gray_data[i] <= bound ? 255 : 0 );
    }
    return 0;
}

int gray_reversed(const uint8_t* gray_data, int width, int height, uint8_t* return_gray_data) {
    if (gray_data == NULL || gray_data == NULL || width <= 0 || height <= 0) {
        return -1; // 或返回错误码
    }

    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; i++) {
        return_gray_data[i] = 255-gray_data[i];
    }
    return 0;
}

// 旋转灰度图90度（顺时针）
int rotate_gray_90_cw(const uint8_t* src, int src_height, int src_width, uint8_t* dst) {
    if (!src || !dst || src_width <= 0 || src_height <= 0) {
        return -1;
    }
    
    // 旋转后尺寸：高度变宽度，宽度变高度
    int dst_width = src_height;
    int dst_height = src_width;
    
    for (int y = 0; y < src_height; y++) {
        for (int x = 0; x < src_width; x++) {
            // 原图坐标 (x, y) -> 旋转后坐标 (src_height-1-y, x)
            int src_idx = y * src_width + x;
            int dst_idx = x * dst_width + (dst_width - 1 - y);
            dst[dst_idx] = src[src_idx];
        }
    }
    return 0;
}

// 旋转灰度图90度（逆时针）
int rotate_gray_90_ccw(const uint8_t* src, int src_height, int src_width, uint8_t* dst) {
    if (!src || !dst || src_width <= 0 || src_height <= 0) {
        return -1;
    }
    
    int dst_width = src_height;
    int dst_height = src_width;
    
    for (int y = 0; y < src_height; y++) {
        for (int x = 0; x < src_width; x++) {
            // 原图坐标 (x, y) -> 旋转后坐标 (y, src_width-1-x)
            int src_idx = y * src_width + x;
            int dst_idx = (dst_height - 1 - x) * dst_width + y;
            dst[dst_idx] = src[src_idx];
        }
    }
    return 0;
}

// 旋转RGB图90度（顺时针）
int rotate_rgb_90_cw(const uint8_t* src, int src_height, int src_width, uint8_t* dst) {
    if (!src || !dst || src_width <= 0 || src_height <= 0) {
        return -1;
    }
    
    int dst_width = src_height;
    int dst_height = src_width;
    
    for (int y = 0; y < src_height; y++) {
        for (int x = 0; x < src_width; x++) {
            int src_pixel_idx = (y * src_width + x) * 3;
            int dst_pixel_idx = (x * dst_width + (dst_width - 1 - y)) * 3;
            
            dst[dst_pixel_idx] = src[src_pixel_idx];          // R
            dst[dst_pixel_idx + 1] = src[src_pixel_idx + 1];  // G
            dst[dst_pixel_idx + 2] = src[src_pixel_idx + 2];  // B
        }
    }
    return 0;
}

// 旋转RGB图90度（逆时针）
int rotate_rgb_90_ccw(const uint8_t* src, int src_height, int src_width, uint8_t* dst) {
    if (!src || !dst || src_width <= 0 || src_height <= 0) {
        return -1;
    }
    
    int dst_width = src_height;
    int dst_height = src_width;
    
    for (int y = 0; y < src_height; y++) {
        for (int x = 0; x < src_width; x++) {
            int src_pixel_idx = (y * src_width + x) * 3;
            int dst_pixel_idx = ((dst_height - 1 - x) * dst_width + y) * 3;
            
            dst[dst_pixel_idx] = src[src_pixel_idx];          // R
            dst[dst_pixel_idx + 1] = src[src_pixel_idx + 1];  // G
            dst[dst_pixel_idx + 2] = src[src_pixel_idx + 2];  // B
        }
    }
    return 0;
}

// 新增函数：文档清理（白底黑字红章 -> 三色图）
int clean_document(const uint8_t* src_rgb, int height, int width,
                   uint8_t* dst_rgb,
                   int red_r_thresh, int red_diff_thresh,
                   int gray_thresh) {
    if (!src_rgb || !dst_rgb || height <= 0 || width <= 0) {
        return -1;
    }

    int total_pixels = height * width;
    for (int i = 0; i < total_pixels; i++) {
        const int src_idx = i * 3;
        uint8_t R = src_rgb[src_idx];
        uint8_t G = src_rgb[src_idx + 1];
        uint8_t B = src_rgb[src_idx + 2];

        // 判断是否为红色（印章）
        int is_red = (R > red_r_thresh) &&
                     ((int)R - (int)G > red_diff_thresh) &&
                     ((int)R - (int)B > red_diff_thresh);

        if (is_red) {
            // 纯红
            dst_rgb[src_idx]     = 255;
            dst_rgb[src_idx + 1] = 0;
            dst_rgb[src_idx + 2] = 0;
        } else {
            // 计算灰度（标准亮度公式）
            int gray = (int)(0.299f * R + 0.587f * G + 0.114f * B);
            if (gray >= gray_thresh) {
                // 白底
                dst_rgb[src_idx]     = 255;
                dst_rgb[src_idx + 1] = 255;
                dst_rgb[src_idx + 2] = 255;
            } else {
                // 黑字
                dst_rgb[src_idx]     = 0;
                dst_rgb[src_idx + 1] = 0;
                dst_rgb[src_idx + 2] = 0;
            }
        }
    }
    return 0;
}

int color_matrix(const uint8_t* src_rgb, int height, int width,
                 uint8_t* dst_rgb, const float color_matrix[9]) {
    if (!src_rgb || !dst_rgb || height <= 0 || width <= 0 || !color_matrix) {
        return -1;
    }

    int total_pixels = height * width;
    for (int i = 0; i < total_pixels; i++) {
        const int idx = i * 3;
        float r = src_rgb[idx];
        float g = src_rgb[idx + 1];
        float b = src_rgb[idx + 2];

        float new_R = r * color_matrix[0] + g * color_matrix[1] + b * color_matrix[2];
        float new_G = r * color_matrix[3] + g * color_matrix[4] + b * color_matrix[5];
        float new_B = r * color_matrix[6] + g * color_matrix[7] + b * color_matrix[8];

        dst_rgb[idx]     = (uint8_t)(new_R < 0 ? 0 : (new_R > 255 ? 255 : new_R));
        dst_rgb[idx + 1] = (uint8_t)(new_G < 0 ? 0 : (new_G > 255 ? 255 : new_G));
        dst_rgb[idx + 2] = (uint8_t)(new_B < 0 ? 0 : (new_B > 255 ? 255 : new_B));
    }
    return 0;
}

int convolution_gray_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge){
    if (!src || !dst || height <= 0 || width <= 0 || !kernel || kernel_edge <=0) {
        return -1;
    }
    if (kernel_edge % 2 == 0) return -1; 
    for (int src_row = 0; src_row < height; src_row++) {
        for (int src_col = 0; src_col < width; src_col++){
            float new_gray = 0;
            for (int kel = 0; kel < kernel_edge*kernel_edge; kel++){
                int row = (kel / kernel_edge - (kernel_edge-1)/2)+src_row;
                int col = (kel % kernel_edge - (kernel_edge-1)/2)+src_col;
                row = row < 0 ? (-row) : (row >= height ? height+height-row-2 : row);
                col = col < 0 ? (-col) : (col >= width ? width+width-col-2 : col);
                new_gray += kernel[kel]*src[row*width + col];
            }
            dst[src_row*width+src_col] = (uint8_t)(new_gray < 0 ? 0 :(new_gray > 255 ? 255 : new_gray));
        }
    }
    return 0;
}

int convolution_rgb_std(const uint8_t* src, int height, int width, uint8_t* dst, const float* kernel, int kernel_edge){
    if (!src || !dst || height <= 0 || width <= 0 || !kernel || kernel_edge <=0) {
        return -1;
    }
    if (kernel_edge % 2 == 0) return -1; 
    for (int src_row = 0; src_row < height; src_row++) {
        for (int src_col = 0; src_col < width; src_col++){
            float new_r = 0;
            float new_g = 0;
            float new_b = 0;
            for (int kel = 0; kel < kernel_edge*kernel_edge; kel++){
                int row = (kel / kernel_edge - (kernel_edge-1)/2)+src_row;
                int col = (kel % kernel_edge - (kernel_edge-1)/2)+src_col;
                row = row < 0 ? (-row) : (row >= height ? height+height-row-2 : row);
                col = col < 0 ? (-col) : (col >= width ? width+width-col-2 : col);
                new_r += kernel[kel]*src[(row*width + col)*3];
                new_g += kernel[kel]*src[(row*width + col)*3+1];
                new_b += kernel[kel]*src[(row*width + col)*3+2];
            }
            dst[(src_row*width+src_col)*3] = (uint8_t)(new_r < 0 ? 0 :(new_r > 255 ? 255 : new_r));
            dst[(src_row*width+src_col)*3+1] = (uint8_t)(new_g < 0 ? 0 :(new_g > 255 ? 255 : new_g));
            dst[(src_row*width+src_col)*3+2] = (uint8_t)(new_b < 0 ? 0 :(new_b > 255 ? 255 : new_b));
        }
    }
    return 0;
}
