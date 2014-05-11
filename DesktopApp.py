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
    subprocess.call("./to_receive_desktop " + file_name, shell=True)
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
    msg = read_server()
    while (msg != "piloaded") and (msg != "cameraoff") and (msg != "picameraoff"):
        time.sleep(4)
    write_server(message="cameraon") 

def arm_sys():
    cv2.namedWindow('Init_img')
    cv2.setMouseCallback('Init_img', onmouse)
    while read_server() != "downloadinitpic" and read_server() != "downloadsnapshot":
        time.sleep(4)
    read_server(file_name="init_pic.jpg")
    init_img = cv2.imread('init_pic.jpg')
    eg.msgbox("To set the target area in the following image, click on the top-left and bottom-right corners of a rectangle that will bound the object. Press 'Enter' and the image will show the selected region. Press 'Enter' again to send target region to Securiot.")
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
        time.sleep(4)
    print "System is now armed"

#Snapshot retrieval
def snapshot():
    write_server(message="requestsnapshot")
    time.sleep(10)
    while read_server() != "downloadsnapshot":
        time.sleep(4)
    read_server(file_name="snapshot.jpg")
    snapshot = cv2.imread('snapshot.jpg')
    cv2.imshow("Snapshot",snapshot)
    ch = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()

def check_for_theft():
    print "Checking for theft"
    if read_server() == "thefttrue" or read_server() == "downloadvideo":
        return True
    return False

def downloadvideo():
    while read_server() != "downloadvideo":
        time.sleep(4)    
    read_server(file_name="before.h264")
    read_server(file_name="after.h264")

def cameraoff():    
    write_server(message="cameraoff")

time1 = 0
sysarm = False

while 1:
    msg ="What would you like to do?"
    title = "Securiot for Desktop"
    if not sysarm:
        choices = ["Turn Camera On", "Arm System", "Take A Snapshot", "Turn Camera Off"]
        choice = eg.choicebox(msg, title, choices)
        if str(choice) == "Turn Camera On":
            eg.msgbox("Camera Turning On")
            cameraon()
            eg.msgbox("Camera Is Now On")
        elif str(choice) == "Arm System":
            eg.msgbox("System is Arming")
            arm_sys()
            sysarm = True
            eg.msgbox("System is now armed. Application will notify you when an alert occurs.")
        elif str(choice) == "Take A Snapshot":
            eg.msgbox("Taking Snapshot")
            snapshot()
        elif str(choice) == "Turn Camera Off":
            eg.msgbox("Turning Camera Off")
            cameraoff()
            eg.msgbox("Camera Off")
    else:
        if check_for_theft():
            eg.msgbox("ALERT: A Theft Has Occured, Downloading Video Now")
            downloadvideo()
            eg.msgbox("Video Downloaded Successfully, Access before.h264 and after.h264, located in the current directory")
            sysarm = False
        time.sleep(10)
    time1 += 1
