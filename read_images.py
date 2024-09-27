import os
import cv2
from src import Reader


def decode_images_in_directory(directory_path):
    reader = Reader()
    for filename in os.listdir(directory_path):
        data_decoded = None
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory_path, filename)
            img = cv2.imread(image_path)
            # 480 640
            crop = img[50:450, 150:600]
            processed_images = reader._process_image(
                image=crop, option=1, ksize_value=3
            )

            for img in processed_images:
                data_decoded = reader._decode_zxingcpp(image=img)
                if data_decoded is not None:
                    print(f"data decoded: {data_decoded}")
                    break

            if data_decoded is not None:
                print(f"data decoded: {data_decoded}")
            else:
                print("No data decoded")
            cv2.imshow("Image", crop)
            cv2.waitKey(100)
            cv2.destroyAllWindows()


# Đường dẫn đến thư mục chứa ảnh mã
directory_path = "./lab"
decode_images_in_directory(directory_path)
