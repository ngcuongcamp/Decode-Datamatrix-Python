import cv2

image = cv2.imread("./lab/65.png")

frame_crop = image[70:350, 120:450]
cv2.imshow("image", frame_crop)
cv2.waitKey(0)
