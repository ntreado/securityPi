# client.py
from Tkinter import *
from time import strftime


def startStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream started")


def stopStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream stopped")


def displayStream():
    listBox.insert(END, strftime("%Y-%m-%d %H:%M:%S")+" -> Stream window opened")

    NewWin = Toplevel(root)
    NewWin.title('Security Stream')
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
    root.destroy()


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
