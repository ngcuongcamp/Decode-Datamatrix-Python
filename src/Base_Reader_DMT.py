import cv2
import numpy as np
from pylibdmtx.pylibdmtx import decode
import zxingcpp
import time


class DMT_Reader:
    def __init__(self):
        # init varialbles
        self.kernel = np.ones((3, 3), np.uint8)
