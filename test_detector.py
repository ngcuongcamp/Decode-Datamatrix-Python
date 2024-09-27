import os
import cv2
from src import Reader

from ultralytics import YOLO
import logging


def decode_images_in_directory(directory_path):
    reader = Reader()
    model = YOLO("qrcode.pt")
    for filename in os.listdir(directory_path):
        data_decoded = None
        logging.getLogger("ultralytics").setLevel(logging.WARNING)
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory_path, filename)
            img = cv2.imread(image_path)
            # 480 640
            crop_1 = img[50:480, 150:600]
            # crop_1 = img[50:470, 200:550]

            # transposed_image = cv2.transpose(crop_1)
            # rotated_image = cv2.flip(transposed_image, flipCode=1)

            # (h, w) = rotated_image.shape[:2]
            # center = (w // 2, h // 2)
            # M = cv2.getRotationMatrix2D(center, 195, 1.0)
            # rotated_image = cv2.warpAffine(rotated_image, M, (w, h))

            # processed_images = reader._process_image(
            #     image=rotated_image, option=1, ksize_value=3
            # )

            # for img in processed_images:
            #     data_decoded = reader._decode_pylibdmtx(image=img)
            #     if data_decoded is not None:
            #         break

            # if data_decoded is not None:
            #     print(f"data decoded: {data_decoded}")
            # else:
            #     print("No data decoded")

            # cv2.imshow("Image1", crop_1)
            # cv2.imshow("rotated_image", rotated_image)
            # if data_decoded is not None:
            #     print(f"data decoded: {data_decoded}")
            #     cv2.waitKey(1)
            # else:
            #     print("No data decoded")
            #     cv2.waitKey(0)
            # cv2.destroyAllWindows()

            height, width = crop_1.shape[:2]
            results = model(crop_1)  # Run YOLOv8 inference on the image
            detections = results[0].boxes  # Get the detections

            for i, detection in enumerate(detections):
                # Get bounding box coordinates
                box = detection.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = box

                cv2.rectangle(crop_1, (x1, y1), (x2, y2), (0, 255, 0), 2)
                x1 = max(0, x1 - 20)
                y1 = max(0, y1 - 20)
                x2 = min(width, x2 + 20)
                y2 = min(height, y2 + 20)

                crop_2 = crop_1[y1:y2, x1:x2]
                transposed_image = cv2.transpose(crop_2)
                rotated_image = cv2.flip(transposed_image, flipCode=1)

                (h, w) = rotated_image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, 195, 1.0)
                rotated_image = cv2.warpAffine(rotated_image, M, (w, h))

                processed_images = reader._process_image(
                    image=rotated_image, option=1, ksize_value=3
                )

                for img in processed_images:
                    data_decoded = reader._decode_pylibdmtx(image=img)
                    if data_decoded is not None:
                        break

                if data_decoded is not None:
                    print(f"data decoded: {data_decoded}")
                else:
                    print("No data decoded")

                cv2.imshow("Image1", crop_2)
                cv2.imshow("roated ", rotated_image)
                if data_decoded is not None:
                    cv2.waitKey(1000)
                else:
                    cv2.waitKey(0)
                cv2.destroyAllWindows()


# Đường dẫn đến thư mục chứa ảnh mã
directory_path = "./lab"
decode_images_in_directory(directory_path)
