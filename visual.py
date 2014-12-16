import numpy as np
import cv2
import sys
import time
import socket
import traceback
import os
import pickle
import json
import threading
import unicodedata

#hostid used if we support multiple cameras
hostid = "myPiCam"
stream_control = False
control_lock = threading.Lock()
shutdown = False

#172.31.174.40
#smae port




def pollContol(cap, data_sock):
    request = "GET /camera/0/events HTTP/1.1\r\n\r\n"
    global stream_control
    global control_lock
    global shutdown
    try:
        host = '172.31.174.40'
        port = 5707
        size = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except Exception, ne:
        print "Error connecting to server: ", ne.message
        print traceback.print_exc()
        sys.exit(-1)
    while True:
        time.sleep(.5)
        control_lock.acquire()
        if shutdown:
            return
        control_lock.release()
        try:
            s.send(request)
            response = s.recv(2048)
            response = response.split("\r\n\r\n")
            mesg = json.loads(response[1])
            print mesg
            if mesg['count'] >= 1:
                for i in mesg['events']:
                    i = unicodedata.normalize('NFKD', i['type']).encode('ascii','ignore')
                    print i + "\n"
                    if "start stream" in i:
                        print "starting stream..."
                        # if stream is already running, then we don't need to start it again
                        control_lock.acquire()
                        print "lock acquired"
                        if stream_control is True:
                            control_lock.release()
                            continue
                        # start stream
                        stream_control = True
                        control_lock.release()
                        print "stream started"

                    elif "stop stream" in i:
                        #end stream
                        print "stopping stream..."
                        control_lock.acquire()
                        print "lock acquired"
                        stream_control = False
                        control_lock.release()
                        cv2.destroyAllWindows()
                        cv2.waitKey(1)
                        print "stream stopped"
                        #after stream_control is set to false, thread will terminate self

        except Exception, ne:
            print "Error getting control response: ", ne.message
            print traceback.print_exc()
            sys.exit(-1)

"""
sendpic -
    Inputs:
        frame: a frame captured via the cv2 library from webcam
        sock: an already opened TCP connection
    Outputs: None
    Purpose:
        sendpic takes a frame,
        encodes it,
        builds an appropriate HTTP header,
        and sends encoded picture over sock
"""
def sendpic(frame, sock):
    #send a frame
    global hostid

    #encode frame
    #default quality = 95, lower to save bandwidth
    quality = int(cv2.IMWRITE_JPEG_QUALITY), 90
    ret, img = cv2.imencode(".jpg", frame, quality)

    if ret:
        imgstr = pickle.dumps(img)
    else:
        print "error converting frame to jpg"
        sys.exit(-1)

    length = len(imgstr)

    #build header
    head = "STREAM " + hostid + " HTTP/1.1\r\n" + "content-type: image/jpeg\r\n" + "content-length: " + str(length) + "\r\n\r\n"
    #print head
    #attach data
    head = head + imgstr
    try:
        #send
        sock.send(head.encode())
        garbage_response = sock.recv(1024)
    except Exception, ne:
        print "error sending HTTP stream"
        print traceback.print_exc()
        sys.exit(-1)

    #how to show frame on revserse side:
    img = pickle.loads(imgstr)
    img = cv2.imdecode(img, cv2.CV_LOAD_IMAGE_COLOR)
    #cv2.imshow('gsfdgysjhdgf', img)
    return

def streamvideo(cap, s):
    global stream_control
    global control_lock

    startTime = time.time()

    try:
        #while we are still reciving video feed,
        while True:
            if time.time() - startTime > 10:
                control_lock.acquire()
		stream_control = False
		control_lock.release()
            time.sleep(.5)
            control_lock.acquire()
            while cap.isOpened() and stream_control is True:
                control_lock.release()
                #grab a frame
                ret, frame = cap.read()
                if ret:
                    #Scale webcam footage to a size reasonable to transmit over network
                    frame = cv2.resize(frame, (320, 240))
                    #send frame
                    #s.send("YOLO".encode())
                    print "Frame Sent"
                    sendpic(frame, s)
                    #cv2.imshow('frame', frame)
                else:
                    print "Error reading webcam input"
                    break
                control_lock.acquire()
            control_lock.release()


    except Exception, ee:
        print "Uknown Error Ocurred in streamvideo(): " + ee.message
        print traceback.print_exc()
        sys.exit(-1)


#cap is a stream of video from the webcam
cap = cv2.VideoCapture(0)

#find the width, height, and framerate of the webcam
w = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.cv.CV_CAP_PROP_FPS))

#print "Width: ", w
#print "Height: ", h


#connect to server
s = None
try:
    host = '172.31.174.40'
    port = 5707
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print "socket opened"
    s.send("POST /camera/0 HTTP/1.1\r\n\r\n")
except Exception, ne:
    print "Error connecting to server: ", ne.message
    print traceback.print_exc()
    sys.exit(-1)

threading.Thread(target=pollContol, args=(cap, s)).start()

try:
    streamvideo(cap,s)
except Exception, ue:
    print "Uknown Error Ocurred: " + ue.message
    print traceback.print_exc()
    sys.exit(-1)
finally:
    # Release everything if job is finished
    print "Closing Resources..."
    #s.close()
    control_lock.acquire()
    stream_control = False
    shutdown = True
    control_lock.release()
    cap.release()
    cv2.destroyAllWindows()
