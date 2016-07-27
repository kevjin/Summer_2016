import Image as Yellow
import cv2
import pytesseract
from sensor_msgs.msg import Image
cv_image=cv2.imread('whitetext.png')
cv2.imwrite('yesman.png',cropped_img)
cv_imagepp=AltImage.open('yesman.png')
print pytesseract.image_to_string(cv_imagepp)
