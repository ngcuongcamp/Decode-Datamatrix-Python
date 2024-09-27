import cv2
import numpy as np
from pylibdmtx.pylibdmtx import decode
import zxingcpp


class Reader:
    def __init__(self):
        super(Reader, self).__init__()

    def _decode_zxingcpp(self, image: np.ndarray):
        # print("running.")
        """
        decode by zxingcpp
        """
        data_decoded = zxingcpp.read_barcodes(image)
        if data_decoded is not None and len(data_decoded) > 0:
            data_decoded = data_decoded[0].text

            if data_decoded is not None:
                print("zxingcpp done: ", data_decoded)
                # return None
                return data_decoded
        # print("None zxingcpp")
        return None

    def _decode_pylibdmtx(self, image: np.ndarray):
        """
        decode by pylibdmtx
        """
        data_decoded = decode(image, timeout=300)
        if data_decoded != []:
            data_decoded = data_decoded[0][0].decode("utf-8")
            if data_decoded is not None:
                print("pylibdmtx done: ", data_decoded)
                # return None
                return data_decoded
        # print("None pylibdmtx")
        return None

    def _process_image(self, image: np.ndarray, option: int, ksize_value: int):
        """
        process image
        `option`: `1`: fill details, `2`: remove details
        """
        try:
            # Kiểm tra ksize_value là số lẻ và lớn hơn 1 cho GaussianBlur
            if ksize_value % 2 == 0 or ksize_value < 1:
                raise ValueError(
                    f"ksize_value should be an odd number and greater than 1, but got {ksize_value}"
                )

            kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (ksize_value, ksize_value)
            )

            if option == 1:
                # Lấp đầy chi tiết
                morph = cv2.dilate(
                    image,
                    cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
                    iterations=1,
                )
                filtered = cv2.GaussianBlur(
                    src=morph, ksize=(ksize_value, ksize_value), sigmaX=0, sigmaY=0
                )
                closing = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel)
                opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
                gray = cv2.cvtColor(closing, cv2.COLOR_BGR2GRAY)

            elif option == 2:
                # Loại bỏ chi tiết
                morph = cv2.erode(
                    image,
                    cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
                    iterations=1,
                )
                filtered = cv2.GaussianBlur(
                    src=morph, ksize=(ksize_value, ksize_value), sigmaX=0, sigmaY=0
                )
                opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
                closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
                gray = cv2.cvtColor(closing, cv2.COLOR_BGR2GRAY)
            return [gray, opening, morph, closing]

        except Exception as e:
            print(f"Error when trying to process image: {e}")
            return []

    def _rotate_image(self, image: np.ndarray, angle: int):
        (h, w) = image.shape[:2]
        (x, y) = w // 2, h // 2
        M = cv2.getRotationMatrix2D((x, y), angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), cv2.INTER_CUBIC)
        return rotated

    def _resize_image(self, image: np.ndarray, value: float):
        (h, w) = image.shape[:2]
        resized = cv2.resize(
            image, (int(w * value), int(h * value))
        )  # Chuyển đổi sang số nguyên
        return resized

    def _loop_threshold(
        self, image: np.ndarray, min_thresh: int, max_thresh: int, step: int
    ):
        """
        Loop through thresholds and try decoding\n
        `image`: gray image
        """
        for threshold in range(min_thresh, max_thresh, step):
            _, thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
            data_decoded = self._decode_zxingcpp(thresh)
            if data_decoded is not None:
                print("_decode_zxingcpp - thresh value: ", threshold)
                return data_decoded
            else:
                print("_decode_pylibdmtx - thresh value: ", threshold)
                data_decoded = self._decode_pylibdmtx(thresh)
                cv2.imshow("thresh", thresh)
                cv2.waitKey(100)
                if data_decoded is not None:
                    return data_decoded
        return None
