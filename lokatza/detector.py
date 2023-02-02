"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""

import requests
import logging
import numpy as np
import cv2
import pytesseract

from lokatza import ip_webcam
from lokatza import player
from lokatza import baseline as baseline_module

NAME = 'Lokatza'
BET_COUNT = 15

Y_BORDER_SIZE = 0
X_BORDER_SIZE = 3

TEMPLATE_FINDING_TEXT = "Finding the bet cells. Put the paper. Click 'Esc' when all cells are green"
FINDING_MARKS = "Finding bet marks..."
MARKS_FOUND_TEXT = "Marks found! Click 'Esc' to continue with the next paper"

cv2.namedWindow(NAME, cv2.WINDOW_NORMAL)

class LearningError(Exception):
    '''
    Learning error exception
    '''

class Detector(object):
    '''
    Detector
    '''

    def __init__(self, url, cyclist_number):
        self._logger = logging.getLogger(__name__)
        self._cyclist_number = cyclist_number
        self._url = url

    def _find_number_cells(self, img):
        y_offset = int(img.shape[1]*0.1)
        y_max_offset = int(img.shape[1]*0.01)
        numbers_chop = img[y_offset:-y_max_offset,0:-1]
        binary = to_binary(numbers_chop)
        return find_cells(binary, filter_checkboxes, -y_offset, 0)

    def _find_id_cell(self, img):
        y_min_offset = int(img.shape[1]*0.05)
        y_offset = int(img.shape[1]*0.2)
        x_offset = int(img.shape[0]*0.6)
        top_right_corner = img[y_min_offset:y_offset,x_offset:-1]
        binary = to_binary(top_right_corner)
        return find_cells(255 - binary, filter_id, y_min_offset, x_offset)

    def find_template(self):
        ip_webcam.focus(self._url)
        while True:
            img = ip_webcam.get_shot(self._url)
            copy = img.copy()

            cells = self._find_number_cells(img)
            color =  (0, 255, 0) if len(cells) == self._cyclist_number else (0,0,255)

            id_cells = self._find_id_cell(img)
            
            add_cells(copy, cells, color)
            add_cells(copy, id_cells, (255, 0, 0))
            add_text(copy, TEMPLATE_FINDING_TEXT)
            cv2.imshow(NAME, copy)

            # Press Esc key to exit
            if cv2.waitKey(1) == 27 and len(cells) == self._cyclist_number and len(id_cells) == 1:
                break

    def learn(self):
        baseline = {}
        img = None
        cells = []
        ip_webcam.focus(self._url)
        while True:
            img = ip_webcam.get_shot(self._url)
            copy = img.copy()

            cells = self._find_number_cells(img)
            color =  (0, 255, 0) if len(cells) == self._cyclist_number else (0,0,255)

            id_cells = self._find_id_cell(img)
            
            add_cells(copy, cells, color)
            add_cells(copy, id_cells, (255, 0, 0))
            cv2.imshow(NAME, copy)

            # Press Esc key to exit
            if cv2.waitKey(1) == 27 and len(cells) == self._cyclist_number and len(id_cells) == 1:
                break

        cells_sorted = sort_cells(cells)  

        for index, cell in enumerate(cells_sorted):
            cell_img = get_cell(img, cell)

            data = pytesseract.image_to_string(cell_img, config="-c tessedit"
                                                        "_char_whitelist=0123456789"
                                                        " --psm 7 digits")
            sanitized = ''.join(filter(str.isdigit, data))
            self._logger.info('New cell digit found: %s', sanitized)

            try:
                baseline[str(index)] = int(sanitized)
            except ValueError:
                continue

        return baseline_module.Baseline(1, baseline)
        
    def run(self, baseline):
        '''
        Run detection
        '''
        img = None
        cells = []
        marked_numbers = []
        ip_webcam.focus(self._url)
        init_threshold = 150
        threshold = init_threshold
        while True:
            img = ip_webcam.get_shot(self._url)
            copy = img.copy()

            cells = self._find_number_cells(img)
            try:
                cells_sorted = sort_cells(cells)
            except IndexError:
                continue

            id_cells = self._find_id_cell(img)
        
            marked_numbers = []
            marked_cells = []
            for index, cell in enumerate(cells_sorted):
                str_index = str(index)
                if str_index not in baseline:
                    continue
                
                cell_img = get_cell(img, cell, threshold)
                # cv2.imshow('Cell', cell_img)
                # cv2.waitKey(0)
                number_of_black_pix = np.sum(cell_img == 0)
                if number_of_black_pix < 50:
                    marked_numbers.append(baseline[str_index])
                    marked_cells.append(cell)

            # Adaptative threshold
            if len(cells) == self._cyclist_number and len(marked_cells) < BET_COUNT:
                threshold = threshold + 5
            elif threshold > 180:
                threshold = init_threshold

            color = (0, 255, 0) if len(marked_cells) == BET_COUNT else (0,0,255)

            add_cells(copy, id_cells, (255, 0, 0))
            add_cells(copy, marked_cells, color)
            
            if len(marked_cells) == BET_COUNT and len(id_cells) == 1:
                add_text(copy, MARKS_FOUND_TEXT)
                cv2.imshow(NAME, copy)
                cv2.waitKey(1)
                break
            else:
                add_text(copy, FINDING_MARKS)
                cv2.imshow(NAME, copy)
                cv2.waitKey(1)

        id_cell = get_cell(img, id_cells[0])
        id_chopped = id_cell[0:-1,int(id_cell.shape[1]*0.5):-1]
        id = pytesseract.image_to_string(id_chopped, config="-c tessedit"
                                                    "_char_whitelist=0123456789"
                                                    " --psm 7 digits")
        id = int(''.join(filter(str.isdigit, id))[-3:])

        cv2.waitKey(0)

        return player.Player(id, "", "", marked_numbers)

def get_cell(image, cell, threshold=128):
    cell_img = image[cell[1]+Y_BORDER_SIZE:cell[1]+cell[3]-Y_BORDER_SIZE,cell[0]+X_BORDER_SIZE:cell[0]+cell[2]-X_BORDER_SIZE]
    resized_img = cv2.resize(cell_img, (cell_img.shape[1]*2, cell_img.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    
    grey_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(grey_img, threshold, 255, cv2.THRESH_BINARY)
    mask = np.zeros(binary_img.shape, dtype=np.uint8)

    cnts = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    cv2.fillPoly(mask, cnts, [255, 255, 255])
    mask = 255 - mask
    final_img = cv2.bitwise_or(binary_img, mask)

    return final_img


def to_binary(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    binary = cv2.adaptiveThreshold(blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 4)

    return binary

def filter_checkboxes(stats, y_offset, x_offset):
    cells = []
    for x,y,w,h,_ in stats[2:]:
        if abs(w - h * 2) < 8:
            cells.append((x-x_offset,y-y_offset,w,h))

    try:
        w_elements = [cell[2] for cell in cells]
        h_elements = [cell[3] for cell in cells]
        w_median = sum(sorted(w_elements)[5:-5]) / (len(w_elements) - 10)
        h_median = sum(sorted(h_elements)[5:-5]) / (len(h_elements) - 10)

        for i, cell in enumerate(cells):
            if abs(w_median-cell[2]) > 10 or abs(h_median-cell[3]) > 10:
                cells.pop(i)
    except ZeroDivisionError:
        pass

    return cells

def filter_id(stats, y_offset, x_offset):
    cells = []
    for x,y,w,h,_ in stats[2:]:
        if abs(w - h * 4) < 15 and w > 50:
            cells.append((x+x_offset,y+y_offset,w,h))

    return cells

def find_cells(image, filter_func, y_offset=0, x_offset=0):
    length = np.array(image).shape[1]
    kernal_h = np.ones((1,length//80), np.uint8)
    kernal_v = np.ones((length//60,1), np.uint8)

    binary_h = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernal_h)
    binary_v = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernal_v)

    combined = binary_h | binary_v

    _, _, stats, _ = cv2.connectedComponentsWithStats(
        combined, connectivity=8, ltype=cv2.CV_32S)

    return filter_func(stats, y_offset, x_offset)

def add_cells(image, cells, color=(0,0,255)):
    for x,y,w,h in cells:
        cv2.rectangle(image, (x,y), (x+w,y+h), color, 1)

def add_text(image, text):
    cv2.putText(image, text, (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

def sort_cells(cells):
    contours = np.array(cells)
    max_height = np.max(np.array(contours)[::, 3])
    # Sort the contours by y-value
    by_y = sorted(contours, key=lambda x: x[1])  # y values

    line_y = by_y[0][1]       # first y
    line = 1
    by_line = []

    # Assign a line number to each contour
    for x, y, w, h in by_y:
        if y > line_y + max_height:
            line_y = y
            line += 1
            
        by_line.append((line, x, y, w, h))

    # This will now sort automatically by line then by x
    return [(x, y, w, h) for _, x, y, w, h in sorted(by_line)]