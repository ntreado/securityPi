"""
File: client.py
Author: Nick Treado
ECE 4564
"""

from Tkinter import *
from time import strftime
import socket
import cv2
import traceback
import pickle
import threading
import time

requestGET = "POTATO /camera/0/snapshot HTTP/1.1\r\n\r\n"
requestTriggerStart = "POST /camera/0/startstream HTTP/1.1\r\n\r\n"
requestTriggerStop = "POST /camera/0/stopstream HTTP/1.1\r\n\r\n"
requestStart = "POST /client/0 HTTP/1.1\r\n\r\n"
requestClose = "DELETE /client/0 HTTP/1.1\r\n\r\n"
stream = True
streamLock = threading.Lock()
frameGlobal = None


def readFrame(s):
    streamLock.acquire()
    f = s.makefile()
    state = 0
    while True:
        i = f.readline()
        if i.lower().startswith('content-length'):
            length = int(i.split(':')[1].strip())
        if i.startswith('\r'):
            state = 2
        else:
            state = 0

        if state is 2:
            frame = f.read(length)
            break

    f.close()
    streamLock.release()
    return frame


def startStreamThread():
    global streamLock
    global stream
    streamLock.acquire()
    if stream is False:
        streamLock.release()
        return
    stream = False
    streamLock.release()
    streamThread = threading.Thread(target=startStream, args=())
    streamThread.daemon = True
    streamThread.start()


def startStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream started")
    button.config(state='disable')
    button3.config(state='normal')
    global stream
    global frameGlobal
    clientsocket.send(requestTriggerStart.encode())
    readFrame(clientsocket)
    while stream is False:
        clientsocket.send(requestGET.encode())

        frame = readFrame(clientsocket)
        frame = pickle.loads(frame)
        frame = cv2.imdecode(frame, cv2.CV_LOAD_IMAGE_COLOR)
        frameGlobal = frame

        cv2.namedWindow("Stream", cv2.CV_WINDOW_AUTOSIZE)
        cv2.startWindowThread()
        cv2.imshow("Stream", frame)

        #streamLock.acquire()
        if stream is True:
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        #streamLock.release()


def stopStream():
    button.config(state='normal')
    button3.config(state='disable')
    clientsocket.send(requestTriggerStop.encode())
    readFrame(clientsocket)
    global streamLock
    global stream
    global frameGlobal
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream stopped")
    streamLock.acquire()
    if stream is True:
        streamLock.release()
        return
    stream = True
    streamLock.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


def takeScreenshot():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Screenshot saved")
    cv2.imwrite('ICUscreenshot.jpg', frameGlobal, [int(cv2.IMWRITE_JPEG_QUALITY), 90])


def exitProgram():
    clientsocket.send(requestClose.encode())
    readFrame(clientsocket)
    stopStream()
    root.destroy()


try:
    host = 'nu.sacst.net'
    port = 5707
    size = 1024
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((host, port))
    clientsocket.send(requestStart.encode())
    readFrame(clientsocket)
except Exception, ne:
    print "Error connecting to server: ", ne.message
    print traceback.print_exc()
    sys.exit(-1)

root = Tk()
root.geometry('500x510+350+70')
root.wm_title("ICU")

title = Label(root, text='Image Capture Unit', font=("Helvetica", 16))

button = Button(root, text='Start Stream', command=startStreamThread)
button2 = Button(root, text='Stop Stream', command=stopStream)
button3 = Button(root, text='Take Screenshot', command=takeScreenshot, state='disable')
button4 = Button(root, text='Exit', command=exitProgram)

logLabel = Label(root, text="Log")

listBox = Listbox(root, width=40)
listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> GUI started")

title.pack(pady=10)
button.pack(pady=10)
button2.pack(pady=10)
button3.pack(pady=10)
logLabel.pack()
listBox.pack()
button4.pack(side=BOTTOM, pady=10)

root.mainloop()
