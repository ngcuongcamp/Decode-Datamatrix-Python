import os
import cv2
from src import Reader
from ultralytics import YOLO
from pyzbar.pyzbar import decode
import numpy as np
import logging

# Initialize the reader from your library
reader = Reader()

# Load YOLOv8 model
model = YOLO("qrcode.pt")
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# Define the directory to save cropped images
crop_dir = "crop"
os.makedirs(crop_dir, exist_ok=True)


def add_padding(x1, y1, x2, y2, padding, image_shape):
    """
    Adds padding to the bounding box coordinates.
    Ensures the padded coordinates are within the image boundaries.
    """
    height, width = image_shape[:2]

    # Calculate new coordinates with padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(width, x2 + padding)
    y2 = min(height, y2 + padding)

    return x1, y1, x2, y2


def decode_qr_barcode(image):
    """
    Tries to decode QR code or barcode from an image.
    Returns the decoded data as a string, or None if no QR code or barcode is found.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image = cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    # Try to decode QR codes or barcodes
    decoded_objects = decode(processed_image)
    for obj in decoded_objects:
        return obj.data.decode("utf-8")  # Return the decoded content

    return None


def decode_images_in_directory(directory_path):
    padding = 10  # Define the padding size

    for filename in os.listdir(directory_path):
        data_decoded = None
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory_path, filename)
            img = cv2.imread(image_path)

            if img is None:
                print(f"Failed to load image: {image_path}")
                continue

            # Process the image using YOLOv8 model
            results = model(img)  # Run YOLOv8 inference on the image
            detections = results[0].boxes  # Get the detections

            if len(detections) == 0:
                print(f"No QR/Barcode detected in {filename}")
                continue

            for i, detection in enumerate(detections):
                # Get bounding box coordinates
                box = detection.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = box

                # Add padding to the bounding box coordinates
                x1, y1, x2, y2 = add_padding(x1, y1, x2, y2, padding, img.shape)

                # Draw bounding box on the image
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Crop the detected object from the image
                cropped_image = img[y1:y2, x1:x2]

                # Decode QR/Barcode from the cropped image
                decoded_content = decode_qr_barcode(cropped_image)

                if decoded_content:
                    print(f"Detected QR/Barcode: {decoded_content}")
                else:
                    # Further process with your reader class
                    processed_images = reader._process_image(
                        image=cropped_image, option=1, ksize_value=3
                    )
                    for img in processed_images:
                        data_decoded = reader._decode_zxingcpp(image=img)
                        if data_decoded:
                            print(f"Data decoded: {data_decoded}")
                            break

                # Save the cropped image
                crop_path = os.path.join(crop_dir, f"{filename}_crop_{i}.png")
                cv2.imwrite(crop_path, cropped_image)

                # Show the cropped image
                cv2.imshow(f"Cropped {i}", cropped_image)

            # Show the image with bounding boxes
            cv2.imshow("YOLOv8 frame", img)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()


# Path to the directory containing the images
directory_path = "./lab"
decode_images_in_directory(directory_path)
