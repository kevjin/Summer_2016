import matplotlib.pyplot as plt
from cv_bridge import CvBridge, CvBridgeError
import numpy as np #For cropping the img
from sensor_msgs.msg import Image
from std_msgs.msg import String
import pytesseract
import rospy
import cv2
#STARTING_COLOR="0" #if higher than 255, return to 0 and start again TO ADD SPACE, I COULD TURN THE REPITIONS INTO FUNCTIONS AND MAKE THE CODE NEATER
#Destroy arrays with less than x pixels
#look up down left right
#use recursion for method, sort of like zombie infection adjacent pixels
#autogenerate arrays and record the number, turn these arrays into images
#zombified pixels can only be zombified once, not twice or more
MAX_HORIZONTAL=640
MAX_VERTICAL=480
rel_up = 479 #relative MAXIMUM values to be changed with every loop, finds max parameters for surface to acqure crop section
rel_down = 0
rel_left = 639  #make BIG values because you want to find less than numbers
rel_right = 0
identify_it= False
def listener():
    # initialize a node called hw2
    rospy.init_node("hw2")
    #pub = rospy.Publisher('EggVision', Float32MultiArray)
    #pub.publish(getDistance())
    #Maybe I have to make this an array, test it out
    #Optimize the threshold for the BSU Turf
    # create a window to display results in
    #cv2.namedWindow("Keypoints", 1)
    #cv2.createTrackbar("min", "Keypoints", 30, 300,nothing)
    #cv2.createTrackbar("max", "Keypoints", 30, 300,nothing)
    # part 2.1 of hw2 -- subscribe to a topic called image
    rospy.Subscriber("camera/rgb/image_color", Image, callback2)
    rospy.Subscriber("camera/depth/image", Image, callback1)
    #self.image_sub=rospy.Subscriber("camera/depth/image", Image, self.callback)
def callback2(data): #RGB -------------------------------------------------------------------------------------------->
    global rel_up
    global rel_down
    global rel_left
    global rel_right
    global identify_it
    """ This is a callback which recieves images and processes them. """
	# convert image into openCV format
    bridge=CvBridge()
      # bgr8 is the pixel encoding -- 8 bits per color, organized as blue/green/red
    cv_image = bridge.imgmsg_to_cv2(data)
    if(identify_it):
	cropped_img=cv_image[rel_up:rel_down, rel_left:rel_right] #You want to run this on rgb, not depth ofc
	#print pytesseract.image_to_string(cropped_img)
	print "This is the REL_UP"	
	print rel_up
	identify_it=False
    cv2.waitKey(10)

def callback1(data): #DEPTH ------------------------------------------------------------------------------------------>
        bridge=CvBridge()
        # bgr8 is the pixel encoding -- 8 bits per color, organized as blue/green/red
	image = bridge.imgmsg_to_cv2(data)   	
	global rel_up
	global rel_down
	global rel_left
	global rel_right
	global identify_it
	THRESHOLD=5
	not_edge= True
	stepBack=True
	x=0
	y=0
	repeats=0
	switch=0
	print "DEBUG: marker 0.5 passed"
	while (not_edge): #keeps looping while the current target is not an edge
		while(switch==0):		
			if(image[x,y]-image[x+1,y]<THRESHOLD and stepBack): #try going right
				if(x<479):				
					x=x+1		#so x will always be one step behind it
				else:
					print "You have reached the end"
				cv2.waitKey(100)
				print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
				if(x>rel_right):
					rel_right=x
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 1 passed"
			elif(image[x,y]-image[x,y+1]<THRESHOLD): #try going down
				y=y+1	#so x will always be one step behind it
				cv2.waitKey(100)
				print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
				if(x>rel_down):
					rel_down=y
					stepBack=True
					print "DEBUG: marker 2 passed"
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
			elif(image[x,y]-image[x-1,y]<THRESHOLD): #try going left MAKE A COMMAND TO NOT GO BACK TO PREVIOUS SQUARES
				x=x-1
				cv2.waitKey(100)
				print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
				if(x<rel_left):
					rel_left=x
					stepBack=False
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 3.5 passed"
			else:
				switch=1
				stepBack=True
				print "DEBUG: marker 4 passed"
				print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
				cv2.waitKey(100)
		while(switch==1):
			if(image[x,y]-image[x-1,y]<THRESHOLD and stepBack):
				x=x-1		#so x will always be one step behind it
				if(x<rel_left):
					rel_left=x
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 5 passed"
					cv2.waitKey(50)
			elif(image[x,y]-image[x,y-1]<THRESHOLD): #try going down
				y=y-1	#so x will always be one step behind it
				if(x<rel_up):
					rel_up=y
					stepBack=True
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 5.5 passed"
			elif(image[x,y]-image[x+1,y]<THRESHOLD): #try going left MAKE A COMMAND TO NOT GO BACK TO PREVIOUS SQUARE	
				x=x+1
				if(x>rel_right):
					rel_right=x
					stepBack=False
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 6 passed"
			else:
				if((rel_right-rel_left)*(rel_down-rel_up)>150): #500 is arbitrarily value, to determine whether size of area is warrant a search or not
					cv2.line(image,(rel_left, rel_up),(rel_right, rel_up),(255,0,0),5)
					cv2.line(image,(rel_left, rel_down),(rel_right, rel_down),(255,0,0),5)
					cv2.line(image,(rel_left, rel_up),(rel_left, rel_down),(255,0,0),5) #Blue Box
					cv2.line(image,(rel_right, rel_up),(rel_right, rel_down),(255,0,0),5)
					identify_it=True
					print str(rel_right) + " , " + str(rel_left) + " , " + str(rel_up) +  " , " + str(rel_down)
					print "DEBUG: marker 7 passed"
					while(identify_it):
						print "Waiting to convert image to text..."
						cv2.waitKey(2000)
				x=rel_right+1
				if(x>640): #Max horizontal pixel size
					x=0
					if repeats!=10: #we cant repeat over 480 pix because screen size is only 480 pix
						repeats=repeats+1 #not sure if repeats++ works in python
					else:
						not_edge=False
				y=47*repeats
				rel_up = 479 #RESESTTING THE VALUES FOR NEXT ITERATION-----------------------------------------------------------------
				rel_down = 0
				rel_left = 639
				rel_right = 0
				stepBack=True
				switch=0
				print "Moved onto next surface"
				cv2.waitKey(100)
	cv2.waitKey(10)
if __name__ == '__main__':
    listener()
    try:  
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down"
    cv2.destroyAllWindows()
