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


import time
import os

import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine
import PySimpleGUI as sg
import numpy as np
    
import gui
    
# 后续可以扩展做其他内容的计算器
def compute(input_path,output_dir,method):
    avaliable_method = {
        'ndvi':compute_ndvi
    }

    if not method in avaliable_method:
        print(f'method:"{method}"is not surpport!')
   
    if not os.path.exists(input_path):
        raise FileNotFoundError('路径不存在')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir,
                            os.path.splitext(os.path.basename(input_path)),
                            '_' + method)
    
    avaliable_method[method](input_path,output_path)


def compute_ndvi(input_path,output_path):

    ##############################
    # 自动寻找近红外波段和红色波段 #
    ##############################
    # 这个饼怕是今年都完不成了

    band_info_list = []
    # 先写个手选gui
    nir_band_index,red_band_index = gui.select_band_GUI(input_path,[NIR,RED],'color_info')

    
    with rasterio.open(input_path) as src:
        profile = src.profile
        nir_band = src.read(nir_band_index)
        red_band = src.read(red_band_index)

    profile.update(dtype=rasterio.float32, count=1)

    nir_band = nir_band.astype(float)
    red_band = red_band.astype(float)

    # 对值进行校正，避免除以零错误
    np.seterr(divide='ignore', invalid='ignore')

    # 计算 NDVI
    ndvi = ratio_difference(nir_band,red_band)
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi, 1)


# 比差值公示很多地方要用，所以也提出来了
def ratio_difference(b1,b2):
    return (b1 - b2) / (b1 + b2)



