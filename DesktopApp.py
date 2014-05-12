import easygui as eg
import sys
import time
import subprocess
import time
import cv2
import numpy as np

topcorner = None
botcorner = None

#Reads the server for the current status and downloads files
def read_server(file_name="info.txt"):
    subprocess.call("./to_receive_desktop " + file_name, shell=True)
    if file_name=="info.txt":
        fil = open(file_name,"r")
        message = fil.readline()
        fil.close()
        print message
        return message
    return None

#Writes status commands to the server and uploads files
def write_server(file_name="info.txt",message=""):
    if file_name == "info.txt":
        fil = open(file_name,"w")
        fil.write(message)
        fil.close()
    subprocess.call("./to_send " + file_name, shell=True)

#Captures mouse input for target region
def onmouse(event, x, y, flags, param):
    global topcorner
    global botcorner
    x, y = np.int16([x, y])
    if event == cv2.EVENT_LBUTTONDOWN and topcorner == None:
        topcorner = (x,y)
    elif event == cv2.EVENT_LBUTTONDOWN:
        botcorner = (x,y)

#Turns the camera on
def cameraon():
    msg = read_server()
    if msg == "downloadinitpic" or msg == "theftfalse" or msg == "downloadvideo":
        eg.msgbox("Camera is already on")
        return
    while (msg != "piloaded") and (msg != "cameraoff") and (msg != "picameraoff"):
        time.sleep(4)
        msg = read_server()
    write_server(message="cameraon") 
    while read_server() != "downloadinitpic":
        time.sleep(4)
    eg.msgbox("Camera Is Now On")
    
#Arms the system to track an object
def arm_sys():
    cv2.namedWindow('Init_img')
    cv2.setMouseCallback('Init_img', onmouse)
    msg = read_server()
    if msg == "theftfalse":
        choices = ["Reset Securiot","Keep Tracking Object"]
        reply = eg.buttonbox("Securiot is already armed, what would you like to do?",choices=choices)
        if reply == "Reset Securiot":
            cameraoff()
            time.sleep(6)
            cameraon()
        else:
            sysarm = True
            return
    elif msg == "picameraoff" or msg == "cameraoff":
        eg.msgbox("Camera is off, Securiot will now turn the camera on and arm system")
        cameraon()
    while msg != "downloadinitpic" and msg != "downloadsnapshot":
        time.sleep(4)
        msg = read_server()
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
    eg.msgbox("Securiot will now calibrate. Please allow about 30 seconds for calibration.")
    while read_server() != "theftfalse":
        time.sleep(4)
    print "System is now armed"

#Retreives a snapshot of the current situation
def snapshot():
    msg = read_server()
    if msg == "picameraoff" or msg == "cameraoff":
        eg.msgbox("Camera is off, Securiot will now turn the camera on")
        cameraon()
    write_server(message="requestsnapshot")
    time.sleep(10)
    while read_server() != "downloadsnapshot":
        time.sleep(4)
    read_server(file_name="snapshot.jpg")
    snapshot = cv2.imread('snapshot.jpg')
    cv2.imshow("Snapshot",snapshot)
    ch = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()

#Checks for a theft if the system is armed
def check_for_theft():
    print "Checking for theft"
    msg = read_server()
    if msg == "thefttrue" or msg == "downloadvideo":
        return True
    return False

#Downloads video from the server
def downloadvideo():
    while read_server() != "downloadvideo":
        time.sleep(4)    
    read_server(file_name="before.h264")
    read_server(file_name="after.h264")

#Turns the camera off
def cameraoff():    
    if read_server() == "picameraoff":
        return
    write_server(message="cameraoff")
    while read_server() != "picameraoff":
        time.sleep(4)

time1 = 0
sysarm = False

#Main loop to show home screen of Securiot for Desktop
while 1:
    msg ="What would you like to do?"
    title = "Securiot for Desktop"
    if not sysarm:
        choices = ["1 Turn Camera On", "3 Arm System", "2 Take A Snapshot", "4 Turn Camera Off / Reset System", "5 Exit"]
        choice = eg.choicebox(msg, title, choices)
        if str(choice) == "1 Turn Camera On":
            eg.msgbox("Camera Turning On")
            cameraon()
        elif str(choice) == "3 Arm System":
            eg.msgbox("System is Arming")
            arm_sys()
            sysarm = True
            eg.msgbox("System is now armed. This application will now run in the background and notify you when an alert occurs.")
        elif str(choice) == "2 Take A Snapshot":
            eg.msgbox("Taking Snapshot")
            snapshot()
        elif str(choice) == "4 Turn Camera Off / Reset System":
            eg.msgbox("Turning Camera Off")
            cameraoff()
            eg.msgbox("Camera Off, Securiot Reset")
        elif str(choice) == "5 Exit":
            eg.msgbox("Turning Camera Off and Exiting")
            cameraoff()
            break
    else:
        if check_for_theft():
            eg.msgbox("ALERT: A Theft Has Occured, Downloading Video Now")
            downloadvideo()
            eg.msgbox("Video Downloaded Successfully, Access before.h264 and after.h264, located in the current directory")
            sysarm = False
        time.sleep(10)
    time1 += 1
