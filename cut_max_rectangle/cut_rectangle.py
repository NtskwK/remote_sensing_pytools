import time
import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine
import PySimpleGUI as sg

def cut(file_path, cropped_file_path):
    with rasterio.open(file_path) as src:
        band_index = 0
        band_data = src.read(band_index+1)
        
        top, bottom, left, right = find_largest_rectangle(band_data)
        
        window = Window(left, top, right - left + 1, bottom - top + 1)
        
        cropped_data = src.read(window=window)
        
        metadata = src.meta
        metadata.update({
            "height": window.height,
            "width": window.width,
            "transform": window_transform(src.transform, window),
        })

    with rasterio.open(cropped_file_path, "w", **metadata) as dest:
        dest.write(cropped_data)

def find_largest_rectangle(image_data):
    mask = (image_data > 0)
    
    left_edges = []
    right_edges = []
    
    for row in mask:
        left_edge = next((i for i, value in enumerate(row) if value), None)
        right_edge = next((i for i, value in enumerate(row[::-1]) if value), None)
        if left_edge is None or right_edge is None:
            left_edges.append(0)
            right_edges.append(0)
        else:
            left_edges.append(left_edge)
            right_edges.append(image_data.shape[1] - right_edge - 1)
    
    max_area = 0
    best_top, best_bottom, best_left, best_right = 0, 0, 0, 0
    
    for top in range(image_data.shape[0]):
        for bottom in range(top, image_data.shape[0]):
            width = min(right_edges[top:bottom + 1]) - max(left_edges[top:bottom + 1]) + 1
            area = width * (bottom - top + 1)
            
            if area > max_area:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time)) + ':找到新的最大矩形' + f'{max_area}', end='\r')
                max_area = area
                best_top, best_bottom = top, bottom
                best_left, best_right = max(left_edges[top:bottom + 1]), min(right_edges[top:bottom + 1])
    
    return best_top, best_bottom, best_left, best_right


def window_transform(transform, window):
    transform_window = Affine.translation(window.col_off, window.row_off) * transform
    return transform_window


def GUI():
    sg.theme('DarkBlue1')

    layout = [    
                [sg.Text('裁剪南北走向面积最大的矩形', font=("Source Han Sans", 28),
                    pad=((10, 50), (50, 50)),justification='center')],
                [sg.Text('选择要裁剪的文件(只支持tif)', font=("Source Han Sans", 16),
                    justification='left')],
                [sg.Input(key='-TIF-'), 
                     sg.FileBrowse(file_types=(('TIF Files', '*.tif'),))],
                [sg.Text('选择输出目录：', font=("Source Han Sans", 16),
                    justification='left')],
                [sg.Input(key='-DIR-'), 
                     sg.FolderBrowse()],
                [sg.Column(
                    [[sg.Button('确定', key='confirm', font=("Source Han Sans", 16), pad=(10, 0)), 
                        sg.Button('取消', key='cancel', font=("Source Han Sans", 16), pad=(10, 0))]],
                    )]
        ]

    window = sg.Window('cut rectangle', layout, default_element_size=(30, 1), size=(None, None))

    while True:
        event, values = window.read(close=False)
        if event == sg.WIN_CLOSED or event == 'cancel':
            quit()

        input, output = [values[x] for x in values]

        start_time = time.time()
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}' + ':任务开始')
        cut(input, output)

        end_time = time.time()

        duration = end_time - start_time

        print('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) + ':\n代码块执行时间:', int(duration), '秒')

    window.close()


if __name__ == '__main__':
    GUI()