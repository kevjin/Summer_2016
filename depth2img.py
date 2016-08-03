import matplotlib.pyplot as plt
from cv_bridge import CvBridge, CvBridgeError
import numpy as np #For cropping the img
from sensor_msgs.msg import Image
from std_msgs.msg import String
import pytesseract
import rospy
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
import cv2
import Image as AltImage
from time import sleep
from math import isnan
mask = np.zeros((480,640), dtype = "uint8")
runTest=0
waitTest=1
def listener():
    rospy.init_node("hw4")
    rospy.Subscriber("camera/depth/image", Image, callback)
    rospy.Subscriber("camera/rgb/image_color", Image, callback2)
    #self.image_sub=rospy.Subscriber("camera/depth/image", Image, self.callback)
def callback2(data):
    global mask
    global runTest
    global waitTest
    """ This is a callback which recieves images and processes them. """
	# convert image into openCV format
    bridge=CvBridge()
      # bgr8 is the pixel encoding -- 8 bits per color, organized as blue/green/red
    rgb_image = bridge.imgmsg_to_cv2(data)
    if(runTest==1):   
        cv2.imshow("Mask", mask)
	cv2.imshow("Applied", cv2.bitwise_and(rgb_image, rgb_image, mask = mask))
	cv2.imwrite("filetester.png",cv2.bitwise_and(rgb_image, rgb_image, mask = mask))
	cv2.waitKey(5000)
	try: 
		cv_imagepp=AltImage.open('filetester.png') #There are sometimes IOErrors, except maybe?
	except IOError:
		print "space doesn't meet requirements"
	waitTest=0
	runTest=0
	print "The text acquired is: " + pytesseract.image_to_string(cv_imagepp)
	sleep(3)
def callback(data): #DEPTH ------------------------------------------------------------------------------------------>
    global mask
    global runTest
    global waitTest
    bridge=CvBridge()
    # bgr8 is the pixel encoding -- 8 bits per color, organized as blue/green/red
    image = bridge.imgmsg_to_cv2(data)
    cv2.imshow("Depth", image)
    #sleep(0.3) greater than 5.0 is white has to be greater than .5 or else its black
    newImage = np.zeros((480, 640, 3), np.uint8)
    newImage[:]=255
    y=0
    x=0
    while(y<475):
	while(x<635):
		if(image[y,x]<5.0 and image[y,x]>0.5):
			newImage[y,x] = int(image[y,x]*51)
		elif(image[y,x]>5.0):
			newImage[y,x]=255
		elif(image[y,x]<0.5 or isnan(image[y,x])):
			newImage[y,x]=0
		else:
			print image[y,x]
		x=x+1
	x=0
	y=y+1
	print y
    cv2.imshow("New Image", newImage)
    cv2.waitKey(100)
    segments = slic(img_as_float(newImage), n_segments = 5, sigma = 5)


    for (i, segVal) in enumerate(np.unique(segments)):
	# construct a mask for the segment
	mask = np.zeros(image.shape[:2], dtype = "uint8")
	print "[x] inspecting segment %d" % (i)
	mask[segments == segVal] = 255
	waitTest=1	
	runTest=1
	while(waitTest==0):
		print "waiting..."
		sleep(1)
	
	cv2.waitKey(50)
if __name__ == '__main__':
    listener()
    try:  
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down"
    cv2.destroyAllWindows()
