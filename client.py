#client.py
from Tkinter import *
from time import strftime
import socket
import cv2
import traceback
import pickle

requestGET = "POTATO /camera/0/snapshot HTTP/1.1\r\n\r\n"
requestTrigger = "POST /sensor/0/trigger HTTP/1.1\r\n\r\n"
requestStart = "POST /client/0 HTTP/1.1\r\n\r\n"
requestClose = "DELETE /client/0 HTTP/1.1\r\n\r\n"


def readFrame(s):
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
    return frame


def startStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream started")
    clientsocket.send(requestTrigger.encode())
    readFrame(clientsocket)
    clientsocket.send(requestGET.encode())

    frame = readFrame(clientsocket)
    frame = pickle.loads(frame)
    frame = cv2.imdecode(frame, cv2.CV_LOAD_IMAGE_COLOR)

    cv2.namedWindow("Stream", cv2.CV_WINDOW_AUTOSIZE)
    cv2.startWindowThread()
    cv2.imshow("Stream", frame)

    #cv2.imshow('frame', frame)
    #cv2.waitKey()


def stopStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream stopped")
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    #clientsocket.send('Stop stream')


def displayStream():

    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream window opened")
    #clientsocket.send('Display stream')

    NewWin = Toplevel(root)
    NewWin.title('ICU Security Stream')
    NewWin.geometry('500x500')
    button3.config(state='disable')

    def quit_win():
        NewWin.destroy()
        button3.config(state='normal')
        listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream window closed")

    QuitButton = Button(NewWin,text='Quit',command=quit_win)
    QuitButton.pack(side=BOTTOM, pady=10)
    NewWin.protocol("WM_DELETE_WINDOW", quit_win) 


def exitProgram():
    clientsocket.send(requestClose.encode())
    readFrame(clientsocket)
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

button = Button(root, text='Start Stream', command=startStream)
button2 = Button(root, text='Stop Stream', command=stopStream)
button3 = Button(root, text='Display Stream', command=displayStream)
button4 = Button(root, text='Exit', command=exitProgram)

logLabel = Label(root, text="Log")

listBox = Listbox(root,width=40)
listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> GUI started")

title.pack(pady=10)
button.pack(pady=10)
button2.pack(pady=10)
button3.pack(pady=10)
logLabel.pack()
listBox.pack()
button4.pack(side=BOTTOM, pady=10)

root.mainloop()
