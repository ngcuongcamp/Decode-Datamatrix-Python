import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Đọc hình ảnh
image = cv2.imread("./lab/20240724_102447.png")

if image is None:
    print("Error: Image not found or unable to read.")
else:
    # Giải mã mã vạch
    decoded_objects = decode(image)

    # Kiểm tra số lượng đối tượng mã vạch được giải mã
    print(f"Number of decoded objects: {len(decoded_objects)}")

    # Xử lý các đối tượng mã vạch đã giải mã
    for obj in decoded_objects:
        # Lấy dữ liệu từ mã vạch
        data = obj.data.decode("utf-8")
        print(f"Decoded data: {data}")

        # Vẽ hình chữ nhật xung quanh mã vạch
        points = obj.polygon
        if len(points) == 4:
            pts = np.array(points, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 2)
        else:
            print("Polygon does not have 4 points, cannot draw rectangle")

    # Hiển thị hình ảnh với mã vạch đã đánh dấu
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
