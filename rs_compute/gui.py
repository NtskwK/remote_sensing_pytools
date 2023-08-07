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

import task

import PySimpleGUI as sg


def main_gui():
    sg.theme('DarkBlue1')

    layout = [
                [sg.Text('NDVI计算器', font=("Source Han Sans", 28),
                         justification='center')],
                [sg.Text('选择要计算的文件(只支持tif)', font=("Source Han Sans", 16),
                         justification='left')],
                [sg.Input(key='-TIF-'), 
                     sg.FileBrowse(file_types=(('TIF Files', '*.tif'),))],
                [sg.Text('选择输出目录：', font=("Source Han Sans", 16),justification='left')],
                [sg.Input(key='-DIR-'), 
                     sg.FolderBrowse()],
                [sg.Button('确定', key='confirm',font=("Source Han Sans", 16),
                           pad=(10, 0)),
                     sg.Button('取消',  key='cancel',font=("Source Han Sans", 16),
                               pad=(10, 0))]
        ]

    window = sg.Window('NDVI compute', layout, default_element_size=(30, 1), size=(None, None))

    while True:
        event, values = window.read(close=False)
        if event == sg.WIN_CLOSED or event == 'CANCEL':
            quit()
        if event == 'confirm':

            
            # log模块要独立出来，不然二级gui的等待时间也会被算进去
            # start_time = time.time()
            # print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}' + ':任务开始')
            
            # start task
            input_path = values['-TIF-']
            output_dir = values['-DIR-']

            # 重构的时候把这里换成main()
            task(input_path,output_dir,'compute','ndvi')

            # end_time = time.time()
            # duration = end_time - start_time
            # print('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) + ':\n代码块执行时间:', int(duration), '秒')

    window.close()


def select_band_gui(self,fp,band_require:list,info:str) -> list:
    if info in tips.keys():
        info = tips[info]
    with rasterio.open(fp) as src:
    # 获取波段数量
        num_bands = src.count

        band_list = []
        band_name_list = []
        # 遍历每个波段
        for i in range(1, num_bands + 1):
            band_name = src.descriptions[i-1]
            if band_name is None:
                band_name = 'Band' + i
            band_name_list.append(band_name)
            bands_list.append({
                'index': i,
                'name': band_name,
                'wavelength': src.tags(i)
            })
            # todo:
            # 有的时候波段的频率会直接写在band_tag里，有条件可以做自动化 

            # 将波段信息添加到 data 字典中


    sg.theme('DarkBlue1')

    layout = []
    layout.append(
            [sg.Text('请选择计算使用的波段', font=("Source Han Sans", 28),justification='center')])
    

    # 建立require数量的选择器
    for i,color in enumerate(band_require):
        layout.append(
            [sg.Text(band)],
            [sg.Listbox(values=band_name_list,key='band' + str(i + 1), size=(30, 6), 
                enable_events=True,default_values=auto_select_color(band_list,color))])


    layout.append(
            [sg.Button('确定', key='confirm',font=("Source Han Sans", 16),
                        pad=(10, 0)),
                sg.Button('取消',  key='cancel',font=("Source Han Sans", 16),
                            pad=(10, 0))],
            [sg.Text(info)])

    window = sg.Window('select band', layout, default_element_size=(30, 1), size=(None, None))

    
    event, values = window.read(close=False)

    if event == sg.WIN_CLOSED or event == 'CANCEL':
        window.close()
        
    if event == 'confirm':
        band_index = []
        for i in range(1,len(values)):
            band_list.append(values['band' + str(i)])

tips = {
    'color_info':'''
                RED:\n
                NIR:\n
                ''',
    }

def auto_select_color(self,bands_list,color_tag):
    color_list = {
        RED:{
            max:'',
            min:'',
        },
        NIR:{
            max:'',
            min:'',
        }
    }

    color_tag = color_tag.upper()
    if not color_tag in color_list.keys():
        return None
    
    color_max = color_list[color_tag][max]
    color_min = color_list[color_tag][min]
    band_within_range = []
    for every_band in bands_list:
        if every_band[wavelength] >= color_max and every_band[wavelength] <= color_min:
            band_within_range.append({
                'wavelength':every_band[wavelength],
                'diff':abs(every_band[wavelength] - (color_max - color_min) / 2)
            })

    min_wavelength_diff = min(band_within_range, key=lambda x: x['wavelength'])['wavelength']
    for every_band in bands_list:
        if every_band[wavelength] == min_wavelength_diff:
            return every_band[index]


if __name__ == '__main__':
    main_gui()