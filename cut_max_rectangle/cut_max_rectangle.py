"""
 Copyright (c) 2023 ZeyuWu

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """


# 用于在遥感影像中裁剪南北走向面积最大的矩形（只支持tif）

import datetime
import rasterio
from rasterio.plot import show
from rasterio.mask import mask
import numpy as np

# 输入路径
file_path = r"path/to/in.tif"
# 输出路径
cropped_file_path = r"path/to/out.tif"

def find_largest_rectangle(image_data):
    # 根据像素值大于零的范围创建布尔掩码
    mask = (image_data > 0)
    
    # 计算每行非零像素连续区域的左右边界
    left_edges = np.argmax(mask, axis=1)
    right_edges = image_data.shape[1] - np.argmax(np.flip(mask, axis=1), axis=1) - 1
    
    max_area = 0
    best_top, best_bottom, best_left, best_right = 0, 0, 0, 0
    
    # 遍历每一行，寻找最大矩形
    for top in range(image_data.shape[0]):
        bottom = top
        for bottom in range(top, image_data.shape[0]):
            # 计算当前行范围内的矩形宽度
            width = np.min(right_edges[top:bottom + 1] - left_edges[top:bottom + 1]) + 1
            
            # 计算当前矩形区域的面积
            area = width * (bottom - top + 1)
            
            # 更新最大矩形的信息
            if area > max_area:
                print(str(datetime.datetime.now())+':找到新的矩形'+f'{max_area}<{area}')
                max_area = area
                best_top, best_bottom = top, bottom
                best_left, best_right = left_edges[top], right_edges[bottom]
    
    return best_top, best_bottom, best_left, best_right


with rasterio.open(file_path) as src:
    # 选择一个波段（这里选择第一个波段，索引从0开始）
    band_index = 0
    band_data = src.read(band_index+1)
    
    # 找到大于零范围内的最大矩形
    top, bottom, left, right = find_largest_rectangle(band_data)
    
    # 定义裁剪窗口
    window = rasterio.windows.Window(left, top, right - left + 1, bottom - top + 1)
    
    # 裁剪影像
    cropped_data = src.read(window=window)
    
    # 更新元数据
    metadata = src.meta
    metadata.update({
        "height": window.height,
        "width": window.width,
        "transform": rasterio.windows.transform(window, src.transform),
    })
    
   
    with rasterio.open(cropped_file_path, "w", **metadata) as dest:
        dest.write(cropped_data)