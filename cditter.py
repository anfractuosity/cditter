#!/usr/bin/python

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np 

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
iopen = cv2.imread('open.jpg',0)
iclosed = cv2.imread('closed.jpg',0)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if not iopen == None and not iclosed == None:
        if np.sqrt(np.sum(np.square(np.subtract(gray,iopen)))) < np.sqrt(np.sum(np.square(np.subtract(gray,iclosed)))):
            print("open")
        else:
            print("closed")

    old = image
    #cv2.imwrite("test.jpg",gray)
    rawCapture.truncate(0)
