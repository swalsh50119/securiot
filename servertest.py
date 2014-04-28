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


cv2.namedWindow('Init_img')
cv2.setMouseCallback('Init_img', onmouse)

while read_server() != "piloaded":
	time.sleep(1)
write_server(message="cameraon") 
#write_server(message="downloadinitpic") #To comment out
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
write_server(message="requestsnapshot")
while read_server() != "downloadsnapshot":
	time.sleep(1)
read_server(file_name="snapshot.jpg")
snapshot = cv2.imread('snapshot.jpg')
cv2.imshow("Snapshot",snapshot)
ch = cv2.waitKey(0) & 0xFF
cv2.destroyAllWindows()
#Upon Theft

while read_server() != "downloadvideo":
	time.sleep(1)

read_server(file_name="before.h264")
read_server(file_name="after.h264")
print "Videos downloaded"
f = raw_input()
write_server(message="cameraoff")



'''
#cv2.imshow("init.jpg")
#write_server(message="target(200,200,400,400)")
#time.sleep(20)
#write_server(message="requestsnapshot")
#read_server(file_name="init_pic.jpg")
#read_server(file_name="before.h264")
#read_server(file_name="after.h264")
#write_server(message="cameraoff")
'''