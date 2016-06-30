#!/usr/bin/python
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np 
from itertools import tee

def window(iterable, size):
    iters = tee(iterable, size)
    for i in range(1, size):
        for each in iters[i:]:
            next(each, None)
    return zip(*iters)


def emit(str):
    global prev
    out = []
    for b in str:
        for i in range(0,8):
            bit = (ord(b) >> i) & 1

            if bit == 0:
                out.append(0)
                out.append(1)
            else:
                out.append(1)
                out.append(0)
    return out

preamble = emit("AZ")

def process(x):
    m = [sum(y) / len(y) for y in zip(*x)][1]

    for i in range(0,len(x)):
        v1=x[i:len(x)]
        new = []
        for v in v1:
            if v[1] > m:
                new.append(v[0])
                new.append(v[0])
            else:
                new.append(v[0])
        if new[0:len(preamble)] == preamble:
            mdec = mancdec(new)
            print("Data: ",tobytes(mdec[0:len(mdec) - (len(mdec) % 16)]))
            break
def binary(arr):
    m = 0
    s = 0
    for o in arr:
        s = s +(o * (2**m))
        m = m + 1
    return s

def mancdec(arr):
    out = []
    for i in range(0,len(arr),2):
        if arr[i:i+2] == [0,1]:
            out.append(0)
        elif arr[i:i+2] == [1,0]:
            out.append(1)
    return out

def tobytes(arr):
    out = ""
    for i in range(0,len(arr),8):
        bits = arr[i:i+8]
        out += chr(binary(bits))
    return out

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=camera.resolution)
 
# allow the camera to warmup
time.sleep(0.1)
 
bits = []

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def extract(data):
    out = []
    x = [0,0]
    c = 0
    old = None

    for d in data:
        c += 1
        x[d] += 1
        if (not old == None and not d == old) or c == len(data):
            if c == len(data):
                out.append((d,x[d]))
            else:
                out.append((d^1,x[d^1]))
                x[d^1] = 0
        old = d

    nout = []
    for o in out:
        if o[1] > 3:
            nout.append(o)


    return nout
    
old = None
trained = False

imgl = []
trainv = []

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    if not old == None and trained == False:
        #print(chr(27) + "[2J")
        print("Training...")
        count = 0
        simid = -1
        simv = float("inf")

        for img in imgl:
            s = mse(gray,img[0])
            if s < simv:
                simid = count
                simv = s

            count += 1
        print("Similarity: ",simv)
        if simv > 2600:
            imgl.append([gray,1])
            simid = len(imgl)-1
        else:
            imgl[simid][1]+=1
            imgl[simid][0] = gray

        trainv = []
        for i in range(0,len(imgl)):
            if imgl[i][1] > 20:
                trainv.append([imgl[i][0],imgl[i][1]])
            if len(trainv) == 2:
                break

        if len(trainv) == 2:
            print("Trained...")
            trained = True        
     
    elif trained:
        simid = -1
        simv = float("inf")
        count = 0
        for img in trainv:
            s = mse(gray,img[0])
            if s < simv:
                simid = count
                simv = s
            count += 1

        trainv[simid][0] = gray
        trainv[simid][1] += 1
        print(chr(27) + "[2J")
        print("Current bit: ",simid)

        bits.append(simid)
        d = extract(bits)
        if len(d) > 8:
            process(d)
    else:
        imgl.append([gray,1])

    old = image        
    rawCapture.truncate(0)
