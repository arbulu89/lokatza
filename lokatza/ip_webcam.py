"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""
import logging
import requests
import numpy as np
import cv2

logging.getLogger('urllib3').setLevel(logging.WARNING)

def focus(url):
    requests.get("{}/focus".format(url))

def get_shot(url):
    img_resp = requests.get("{}/shot.jpg".format(url))
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    return cv2.imdecode(img_arr, -1)