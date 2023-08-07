import time
import logging
import rasterio
import numpy as np
import PySimpleGUI as sg

from rasterio.transform import Affine
from rasterio.windows import Window

def crop_and_save_tiff(tiff_path, output_path):
    try:
        with rasterio.open(tiff_path) as dataset:
            num_bands = dataset.count
            metadata = dataset.meta

            all_bands_data = []
            for i in range(1, num_bands+1):
                band_data = dataset.read(i)
                all_bands_data.append(band_data)

            stacked_data = np.stack(all_bands_data, axis=0)
            mask = np.all(stacked_data > 0, axis=0)
            cropped_data = stacked_data[:, mask]

            metadata.update(count=cropped_data.shape[0], height=cropped_data.shape[1], width=cropped_data.shape[2])

            with rasterio.open(output_path, 'w', **metadata) as output_dataset:
                for i, band_data in enumerate(cropped_data, start=1):
                    output_dataset.write(band_data, i)

        logging.info('mission compelet!')

    except Exception as e:
        logging.error(f'error: {str(e)}')


def cut_rectangle(file_path, cropped_file_path):
    try:
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

        logging.info('mission compelet!')

    except Exception as e:
        logging.error(f'error: {str(e)}')


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
                logging.info(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) + ':the largest rectangle' + f'{max_area}')
                max_area = area
                best_top, best_bottom = top, bottom
                best_left, best_right = max(left_edges[top:bottom + 1]), min(right_edges[top:bottom + 1])

    return best_top, best_bottom, best_left, best_right


def window_transform(transform, window):
    transform_window = Affine.translation(window.col_off, window.row_off) * transform
    return transform_window


logging.basicConfig(filename='progress.log', level=logging.INFO, format='%(asctime)s %(message)s')

layout = [
    [sg.Text('Select the GeoTIFF file:')],
    [sg.Input(key='-INPUT-', enable_events=True), sg.FileBrowse(file_types=(("TIFF Files", "*.tif"),))],
    [sg.Text('Output:')],
    [sg.Input(key='-OUTPUT-'), sg.FileSaveAs(file_types=(("TIFF Files", "*.tif"),))],
    [sg.Checkbox('Cut to a north-south rectangle', key='-CROP-', default=False)],
    [sg.Button('Apply')]
]

window = sg.Window('GeoTIFF Clipper', layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == 'Apply':
        input_file = values['-INPUT-']
        output_file = values['-OUTPUT-']
        crop_rectangular = values['-CROP-']

        if not (input_file and output_file):
            sg.popup('Please select the input and output file paths!')

        try:
            if crop_rectangular:
                cut_rectangle(input_file, output_file)
            else:
                crop_and_save_tiff(input_file, output_file)
            sg.popup('mission compelet!')

        except Exception as e:
            sg.popup(f'error: {str(e)}')

        logging.info('mission compelet!')

window.close()
