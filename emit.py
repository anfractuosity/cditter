#!/usr/bin/python
import os
import time

# Start with CD tray closed
os.system("eject -t")
time.sleep(15)
os.system("eject -T")
time.sleep(15)
os.system("eject -t")
time.sleep(15)

prev = 0

def emit(str):
    global prev

    for b in str:
        for i in range(0,8):
            bit = (ord(b) >> i) & 1 
            
            if bit == 0:
                manc = [0,1]
            else:
                manc = [1,0]

            for bv in manc:            
                print(bv)
                if bv == 1:
                    if not prev == 1:
                        os.system("eject -T")
                    time.sleep(4)
                else:
                    os.system("eject -t")
                    time.sleep(4)
                prev = bv

emit("AZhello")
