import matplotlib.pyplot as plt
'''
Boise State University 

Advisor: Dr. Elisa Barney Smith
Author: Kevin Jin
'''
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
import math
mask = np.zeros((imageHeight,imageWidth), dtype = "uint8")
#mask=np.full((480,640),255,dtype="uint8")
runTest=0
waitTest=1
textList=[]
runFinal=0
imageWidth = 0
imageHeight = 0
def listener():
    rospy.init_node("hw4")
    rospy.Subscriber("camera/depth/image", Image, callbackDEPTH)
    rospy.Subscriber("camera/rgb/image_color", Image, callbackRGB)
    #self.image_sub=rospy.Subscriber("camera/depth/image", Image, self.callback)
def callbackRGB(data):     """ This is a callback which recieves the RGB images and processes them. """
    global mask
    global runTest
    global waitTest
    global textList
    global runFinal
    global imageWidth
    global imageHeight


	# convert ROS Image Format into openCV's IPlImage
    bridge=CvBridge()
    rgb_image = bridge.imgmsg_to_cv2(data)
    if(runTest==1):
	rgb_image = cv2.medianBlur(rgb_image,5)
	rgb_imageG = cv2.cvtColor( rgb_image, cv2.COLOR_RGB2GRAY ) 
	th3 = cv2.adaptiveThreshold(rgb_imageG,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\ 
cv2.THRESH_BINARY,11,2) #adaptive gaussion threshold
        cv2.imshow("Mask", mask)
	cv2.imshow("Final Product", cv2.bitwise_and(th3, th3, mask = mask))
	cv2.imwrite("filetester.png",cv2.bitwise_and(th3, th3, mask = mask)) #This method converts to the image pytesser needs
	cv2.imshow("th3", th3)
	cv2.waitKey(5000)
	try: 
		cv_imagepp=AltImage.open('filetester.png') #IOErrors occur if the image doesn't exist
	except IOError:
		print "space doesn't meet requirements"
	waitTest=0 #breaks out of the while loop in the other callback
	runTest=0
	print "The text acquired is: " + pytesseract.image_to_string(cv_imagepp)
	if (pytesseract.image_to_string(cv_imagepp)):
		textList.append(pytesseract.image_to_string(cv_imagepp))
	sleep(3)
    if(runFinal==1):
	rgb_image = cv2.medianBlur(rgb_image,5)
	rgb_imageG = cv2.cvtColor( rgb_image, cv2.COLOR_RGB2GRAY ) 
	th3 = cv2.adaptiveThreshold(rgb_imageG,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
cv2.THRESH_BINARY,11,2)
	cv2.imwrite("th3.png",th3)
	try: 
		tth3=AltImage.open('th3.png')
	except IOError:
		print "space doesn't meet requirements"
	runFinal=0 #The below is to compare how the program fares without segmenting our image and with
	print "--------------------------------------------------"
	print "--------------------------------------------------"
	print "Without Surfaces: "+pytesseract.image_to_string(tth3)
	print "--------------------------------------------------"
	print "--------------------------------------------------"
	for text in textList:
		print "With Surfaces: "+ text
	print "--------------------------------------------------"
	print "--------------------------------------------------"
	textList=[]
def callbackDEPTH(data): """ This is a callback which recieves the DEPTH map and processes it. """
    global mask
    global runTest
    global waitTest
    global runFinal
    global imageWidth
    global imageHeight
    bridge=CvBridge() #This is the bridge to convert to IplImage
    image = bridge.imgmsg_to_cv2(data)
    imageHeight, imageWidth = image.shape[:2]
    cv2.imshow("Depth Map Raw", image)
    newImage = np.zeros((imageHeight, imageWidth, 3), np.uint8) 
    newImage[:]=255 #The Grayscale Equivalent (Depth) is now being created
    y=0
    x=0
    while(y<imageHeight):
	while(x<imageWidth):
		if(image[y,x]<5.0 and image[y,x]>0.5):
			newImage[y,x] = int(image[y,x]*51)
		elif(image[y,x]>5.0):
			newImage[y,x]=255
		elif(image[y,x]<0.5 or math.isnan(image[y,x])):
			newImage[y,x]=1 #We're leaving pixel intensity values = 0 for our mask
		else:
			print image[y,x]
		x=x+1
	x=0
	y=y+1
    cv2.imshow("ConvertedDepthMap", newImage) #This is the Grayscale equivalent
    cv2.waitKey(100)
    segments = slic(img_as_float(newImage), n_segments = 3, sigma = 5) #Can change the number of superpixels with n_segments


    for (i, segVal) in enumerate(np.unique(segments)):
	# constructs a mask for the segment
	mask = np.zeros(image.shape[:2], dtype = "uint8")
	print "[x] inspecting segment %d" % (i)
	mask[segments == segVal] = 255
	sigmaTest = cv2.bitwise_and(newImage, newImage, mask = mask) #Running our standard deviation test
	sigmaTest=cv2.cvtColor(sigmaTest,cv2.COLOR_BGR2GRAY)
        totalMean = 0
        unmaskedArea = 0
        for (x,y), value in np.ndenumerate(sigmaTest):
    	    if(sigmaTest[x,y]!=0): #we don't want a complete 255 black because we know that's our mask
                totalMean = totalMean + int(sigmaTest[x,y])
	        unmaskedArea = unmaskedArea +1

        mean = int(totalMean/unmaskedArea)
        print "mean: " + str(mean)
        totalVar = 0
        for (x,y), value in np.ndenumerate(sigmaTest):
  	    if(sigmaTest[x,y]!=0):
                totalVar = totalVar + math.pow(abs(int(sigmaTest[x,y])-mean),2)
        sigmaVal = int(math.sqrt(totalVar/unmaskedArea))
        print "SIGMA IS: "+ str(sigmaVal) +" for " + str(i)
	cv2.imshow("SigmaTest",sigmaTest)
	cv2.waitKey(5000)
	sleep(3)
	if(sigmaVal < 40): # If the standard deviation is less than 40, proceed with running superpixels on it
  		waitTest=1 #This is a switch which allows the other callback to apply the mask to the RGB image	
		runTest=1
	while(waitTest==1): #Waits for the other callback to finish running everything with the RGB image
		print "waiting..."
		sleep(1)
	
	cv2.waitKey(50)
    runFinal=1 #Run final is running the text recognition on the entire image, without superpixels
    while(runFinal==1):
	print "waiting for a bit..."
	sleep(1)
if __name__ == '__main__':
    listener()
    try:  
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down"
    cv2.destroyAllWindows()
