# save this file as ......| test1.py
# run this file this way..| python  test1.py
import easygui as eg
import sys
import time
import subprocess
import time
import cv2
import numpy as np

topcorner = None
botcorner = None

def read_server(file_name="info.txt"):
    subprocess.call("./to_receive " + file_name, shell=True)
    if file_name=="info.txt":
        fil = open(file_name,"r")
        message = fil.readline()
        fil.close()
        print message
        return message
    return None

def write_server(file_name="info.txt",message=""):
    if file_name == "info.txt":
        fil = open(file_name,"w")
        fil.write(message)
        fil.close()
    subprocess.call("./to_send " + file_name, shell=True)

def onmouse(event, x, y, flags, param):
    global topcorner
    global botcorner
    x, y = np.int16([x, y])
    if event == cv2.EVENT_LBUTTONDOWN and topcorner == None:
        topcorner = (x,y)
    elif event == cv2.EVENT_LBUTTONDOWN:
        botcorner = (x,y)

def cameraon():
    while read_server() != "piloaded":
        time.sleep(1)
    write_server(message="cameraon") 

def arm_sys():
    #write_server(message="downloadinitpic") #To comment out
    cv2.namedWindow('Init_img')
    cv2.setMouseCallback('Init_img', onmouse)
    while read_server() != "downloadinitpic":
        time.sleep(1)
    read_server(file_name="init_pic.jpg")
    init_img = cv2.imread('init_pic.jpg')
    cv2.imshow("Init_img",init_img)
    ch = cv2.waitKey(0) & 0xFF
    x0, y0 = topcorner
    x1, y1 = botcorner
    cv2.rectangle(init_img,(x0, y0), (x1, y1), 150,3)
    cv2.imshow("Init_img",init_img)
    ch = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    target = "target"+ str((x0,y0,x1,y1))
    write_server(message=target)
    while read_server() != "theftfalse":
        time.sleep(1)
    print "System is now armed"

#Snapshot retrieval
def snapshot():
    write_server(message="requestsnapshot")
    while read_server() != "downloadsnapshot":
        time.sleep(1)
    read_server(file_name="snapshot.jpg")
    snapshot = cv2.imread('snapshot.jpg')
    cv2.imshow("Snapshot",snapshot)
    ch = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()

def check_for_theft():
    print "in check_for_theft"
    if read_server() == "downloadvideo":
        downloadvideo()

def downloadvideo():
    read_server(file_name="before.h264")
    read_server(file_name="after.h264")
    return "Videos downloaded"

def cameraoff():    
    write_server(message="cameraoff")

time1 = 0

while 1:
    msg ="What would you like to do"
    title = "Securiot for Desktop"
    choices = ["Turn Camera On", "Arm System", "Take A Snapshot", "Turn Camera Off"]
    if time1 % 2 == 0:
        check_for_theft()
    choice = eg.choicebox(msg, title, choices)
    if str(choice) == "Turn Camera On":
        eg.msgbox("Camera Turning On")
        cameraon()
        eg.msgbox("Camera In Now On")
    elif str(choice) == "Arm System":
        eg.msgbox("System is Arming")
        arm_sys()
        eg.msgbox("System is now armed")
    elif str(choice) == "Take A Snapshot":

        snapshot()
        eg.msgbox("Retrieving snapshot")
    elif str(choice) == "Turn Camera Off":
        cameraoff()

    msg = "Do you want to continue?"
    title = "Please Confirm"
    if eg.ccbox(msg, title):     # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        sys.exit(0)           # user chose Cancel
    time1 += 1
