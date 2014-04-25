#!/usr/bin/env python
import numpy as np
import cv2
import video
import sys
import smtplib
import time
from PIL import Image
import io
import picamera
import os

#  Securiot: The Future of Surveillance
#   -Goal: Detect theft of objects from a desk and alert user

# Server(Android/User) to App communication
# Camera On/Off - turns on the camera
#   Set Phone number
# Focus Region - (x0,y0,x1,y1) region for focus
# Retrieve current snapshot

# App to Server(User)
# Camera On/Off Response
# Tracking State
# Theft Videos
# Upload Current snapshot

def nothing(*arg):
    pass

class App(object):
    def __init__(self, video_src,):

        #Paramters to tune
        self.calib_len = 20
        self.var_scale = 2
        
        #Initialization
        self.temp_area = [[]]
        self.calib = [0]
        self.ref_img = [None]
        self.area_mean = [0]
        self.area_var = [0]
        self.check_num = [0]
        self.stolen = [0]

        self.selection = [(150,180,300,300)]
        self.curr_selection = None
        self.drag_start = None
        self.init_img_sent = False
        self.tracking_state = 0
        self.memory = []
        self.steal_mem=[]

    #Take picture and convert into CV2 format
    def take_pic(self,camera):
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        current_image = Image.open(stream)
        img = cv2.cvtColor(np.asarray(current_image), cv2.COLOR_RGB2BGR)
        return img

    #Write the entire circular buffer to disk
    def write_video(self,stream):
        with io.open('before.h264', 'wb') as output:
            for frame in stream.frames:
                if frame.header:
                    stream.seek(frame.position)
                    break
            while True:
                buf = stream.read1()
                if not buf:
                    break
                output.write(buf)
        stream.seek(0)
        stream.truncate()

    #Send the initial image for focus region ID
    def send_first(self,img):
        cv2.imwrite('init_pic.jpg',img)
        self.init_img_sent = True
        print 'ref img sent'

    #Add another focus region in the scene
    def add_focus(self):
        self.temp_area.append([])
        self.calib.append(0)
        self.ref_img.append(None)
        self.area_mean.append(0)
        self.area_var.append(0)
        self.stolen.append(0)
        self.check_num.append(0)

    #Remove a focus region from the scene
    def rm_focus(self,i):
        self.check_num.pop(i)
        self.stolen.pop(i)
        self.temp_area.pop(i)
        self.calib.pop(i)
        self.ref_img.pop(i)
        self.area_mean.pop(i)
        self.area_var.pop(i) 
        self.selection.pop(i)     

    #Send a SMS text to user if a security event takes place
    def send_sms(self):
        server = smtplib.SMTP( "smtp.gmail.com", 587 )
        server.starttls()
        server.login( 'securiotalert@gmail.com', 'securiot144r' )
        server.sendmail( 'securiotalert@gmail.com', '8457751342@messaging.sprintpcs.com', 'ALERT, Securiot has detected a security event' )

    #Do this once a steal is registered
    def on_steal(self,i):
        print "ALERT"
        #App.send_sms(self)

    #Check the focus region for change in object location
    def check_obj(self,area_arr,i):
        #Print image of stolen item
        if self.stolen[i] == 1:
            diff_img = cv2.absdiff(self.frame,self.ref_img[i])
            diff_img_mask = cv2.cvtColor(diff_img,cv2.COLOR_BGR2GRAY)
            tf, diff_img_mask = cv2.threshold(diff_img_mask,50,255,cv2.THRESH_BINARY)
            stolen = cv2.bitwise_and(self.ref_img[i],self.ref_img[i],mask=diff_img_mask)
            stolen = cv2.addWeighted(stolen,.95,self.ref_img[i],.05,10)
            #winname = 'Stolen Item' + str(i)
            #cv2.imshow(winname, stolen)
        #Calibrate the image to the target region
        elif self.calib[i] < self.calib_len:
            self.temp_area[i].append(sum(area_arr[-4:]))
            self.calib[i] += 1
            print self.calib[i]
            return False
        #Store averaged values for the calibration period
        elif self.calib[i] == self.calib_len:
            self.ref_img[i] = np.copy(self.frame)
            self.area_mean[i] = np.mean(self.temp_area[i])
            self.area_var[i] = np.std(self.temp_area[i])
            if self.var_scale*self.area_var[i] > self.area_mean[i]*0.15:
                self.check_num[i] = self.var_scale*self.area_var[i]
            else:
                self.check_num[i] = self.area_mean[i]*0.15
            print self.area_mean
            print self.check_num
            self.calib[i] += 1
            return False
        #Check current values versus calibration phase
        elif self.calib[i] > self.calib_len and not self.stolen[i]:
            self.temp_area[i].pop(0)
            self.temp_area[i].append(sum(area_arr[-4:]))
            if abs(np.mean(self.temp_area[i])-self.area_mean[i]) > self.check_num[i]:
                self.stolen[i] = 1
                #App.on_steal(self,i)
                return True
            return False

    #Main function for the application
    def run(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            stream = picamera.PiCameraCircularIO(camera, seconds=2)
            camera.start_recording(stream, format='h264')
            while True:
                camera.wait_recording(0.3)
                self.frame = App.take_pic(self,camera)
                #Send initial image for target location
                if not self.init_img_sent:
                    App.send_first(self,self.frame)
                    #Wait for response from user
                    #App.check_server()
                if self.selection:
                    for s in self.selection:
                        ind = self.selection.index(s)
                        x0, y0, x1, y1 = s
                        focus = self.frame[y0:y1,x0:x1]
                        img = cv2.cvtColor(focus, cv2.COLOR_BGR2GRAY)
                        edges = cv2.Canny(img, 2000, 200, apertureSize=5)
                        kernel = np.ones((3,3),np.uint8)
                        edges = cv2.dilate(edges,kernel,iterations = 2)
                        preview = self.frame #np.copy(self.frame)
                        contours, hier = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE,offset=(x0,y0))
                        area_arr = []
                        for cnt in contours:
                            hull = cv2.convexHull(cnt)
                            area_arr.append(cv2.contourArea(hull))
                            cv2.fillConvexPoly(preview,hull,(255,255,100))
                        area_arr.sort()
                        if App.check_obj(self,area_arr,ind):
                            print 'Alert, object stolen!'
                            camera.split_recording('after.h264')
                            # Write the 10 seconds "before" motion to disk
                            App.write_video(self,stream)
                            # Record 10s after steal
                            camera.wait_recording(10)
                            camera.split_recording(stream)
                            rm_focus(self,ind)
                        winname = 'Focus' + str(ind)
                        cv2.imshow(winname,preview)
                ch = 0xFF & cv2.waitKey(1)
                if ch == 27:
                    break
            cv2.destroyAllWindows()
            camera.stop_recording()

if __name__ == '__main__':
    #import socket
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.bind(("localhost", 9988))
    #s.listen(1)
    #conn, addr = s.accept()
    #data = conn.recv(1024)
    #conn.close()
    #print data
    import sys
    try: video_src = sys.argv[1]
    except: video_src = 0
    print __doc__
    App(video_src).run()