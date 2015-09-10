import cv2
#import numpy as np
from Scanner import Scanner
from TopCode import TopCode


scan = Scanner()


cam = cv2.VideoCapture(0)


if not cam.isOpened():
	raise Exception("No camera detected!")

while True:
	ret, image = cam.read()
	cv2.imshow("img", image)
	cv2.waitKey(1)

	if(image is not None):
		spots = scan.scan(image = image)
		print "Detected " + str(len(spots)) + " targets"
