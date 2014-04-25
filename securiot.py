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
import glob

#  Goals of the algorithm
#1 Detect the removal of a target object from the focus area
#2 Don't alert on detection of objects moving through the target area

# How
#1 Canny Edge Detection to find edges of the device of interest.
#2 Find shape of device in image, check aspects of the contour over time

# Input Usage
# Camera On - turns on trakcing software
# Select target region(s)


def nothing(*arg):
    pass

class App(object):
    def __init__(self, video_src,):
        #self.cam = video.create_capture(video_src)
        #stream = io.BytesIO()
        #with picamera.PiCamera() as camera:
        #    camera.resolution = (640,480)
        #    camera.capture(stream,format='jpeg')
        #data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        #self.frame=cv2.imdecode(data,1)

        #ret, self.frame = self.cam.read()
        #self.cam = cv2.VideoCapture('video_1.mkv')
        #cv2.namedWindow('Camera View')
        #cv2.setMouseCallback('Camera View', self.onmouse)
        #cv2.createTrackbar('thrs1', 'edge', 2000, 5000, nothing)
        #cv2.createTrackbar('thrs2', 'edge', 200, 3000, nothing)

        #Paramters to tune
        self.calib_len = 10
        self.var_scale = 2
        self.memory_max_len = 5

        self.temp_area = [[]]
        self.calib = [0]
        self.ref_img = [None]
        self.area_mean = [0]
        self.area_var = [0]
        self.check_num = [0]
        self.stolen = [0]

        self.selection = [(200,200,400,400)]
        self.curr_selection = None
        self.drag_start = None
        self.tracking_state = 1
        self.memory = []
        self.steal_mem=[]

        files = glob.glob('./memory/*')
        for f in files:
            os.remove(f)

    def take_pic(self,camera):
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        current_image = Image.open(stream)
        img = cv2.cvtColor(np.asarray(current_image), cv2.COLOR_RGB2BGR)
        return img

    def add_memory(self):
        files = glob.glob('./memory/*')
        files_sort = sorted(files, key=os.path.getmtime)
        if len(files) > self.memory_max_len:
            os.remove(files_sort[0])
        self.memory.append(np.copy(self.frame))
        name = 'memory/' + str(int(time.time())) + '.jpg'
        cv2.imwrite(name,self.frame)


    def add_focus(self):
        self.temp_area.append([])
        self.calib.append(0)
        self.ref_img.append(None)
        self.area_mean.append(0)
        self.area_var.append(0)
        self.stolen.append(0)
        self.check_num.append(0)

    def rm_focus(self,i):
        self.check_num.pop(i)
        self.stolen.pop(i)
        self.temp_area.pop(i)
        self.calib.pop(i)
        self.ref_img.pop(i)
        self.area_mean.pop(i)
        self.area_var.pop(i) 
        self.selection.pop(i)     

    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y]) # BUG
        if event == cv2.EVENT_LBUTTONDOWN:
            App.add_focus(self)
            self.drag_start = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            if self.curr_selection is not None:
                self.tracking_state = 1
                self.selection.append(self.curr_selection)
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frame.shape[:2]
                xo, yo = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
                self.curr_selection = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.curr_selection = (x0, y0, x1, y1)

    def send_sms(self):
        server = smtplib.SMTP( "smtp.gmail.com", 587 )
        server.starttls()
        server.login( 'securiotalert@gmail.com', 'securiot144r' )
        server.sendmail( 'securiotalert@gmail.com', '8457751342@messaging.sprintpcs.com', 'ALERT, Securiot has detected a security event' )

    def on_steal(self,i):
        print "ALERT"
        #App.send_sms(self)
        self.steal_mem.append(np.copy(self.memory))
        #for img in self.steal_mem[i]
        print 'just copied' 
        cv2.imshow('Recording of Theft',self.steal_mem[0])
        ch = 0xFF & cv2.waitKey(0)


    def check_obj(self,area_arr,i):
        if self.stolen[i] == 1:
            diff_img = cv2.absdiff(self.frame,self.ref_img[i])
            diff_img_mask = cv2.cvtColor(diff_img,cv2.COLOR_BGR2GRAY)
            tf, diff_img_mask = cv2.threshold(diff_img_mask,50,255,cv2.THRESH_BINARY)
            stolen = cv2.bitwise_and(self.ref_img[i],self.ref_img[i],mask=diff_img_mask)
            stolen = cv2.addWeighted(stolen,.95,self.ref_img[i],.05,10)
            #winname = 'Stolen Item' + str(i)
            #cv2.imshow(winname, stolen)
        elif self.calib[i] < self.calib_len:
            self.temp_area[i].append(sum(area_arr[-4:]))
            self.calib[i] += 1
            print self.calib[i]
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
        elif self.calib[i] > self.calib_len and not self.stolen[i]:
            self.temp_area[i].pop(0)
            self.temp_area[i].append(sum(area_arr[-4:]))
            if abs(np.mean(self.temp_area[i])-self.area_mean[i]) > self.check_num[i]:
                self.stolen[i] = 1
                App.on_steal(self,i)
                #Call Alert function

    def run(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            stream = picamera.PiCameraCircularIO(camera, seconds=10)
            camera.start_recording(stream, format='h264')
            while True:
                camera.wait_recording(0.5)
                self.frame = App.take_pic(self,camera)
                #if not self.selection and not self.tracking_state:
                    #App.send_first()
                if self.selection and self.tracking_state:
                    for s in self.selection:
                        ind = self.selection.index(s)
                        x0, y0, x1, y1 = s
                        focus = self.frame[y0:y1,x0:x1]
                        img = cv2.cvtColor(focus, cv2.COLOR_BGR2GRAY)
                        thrs1 = 2000 #cv2.getTrackbarPos('thrs1', 'Camera View')
                        thrs2 = 200 #cv2.getTrackbarPos('thrs2', 'edge')
                        edges = cv2.Canny(img, thrs1, thrs2, apertureSize=5)
                        kernel = np.ones((3,3),np.uint8)
                        edges = cv2.dilate(edges,kernel,iterations = 2)
                        preview = self.frame #np.copy(self.frame)
                        contours, hier = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE,offset=(x0,y0))
                        area_arr = []
                        for cnt in contours:
                            #area_arr.append(cv2.contourArea(cnt))
                            hull = cv2.convexHull(cnt)
                            area_arr.append(cv2.contourArea(hull))
                            #cv2.drawContours(preview, cnt, -1,(255,0,255),4,offset=(x0,y0))
                            cv2.fillConvexPoly(preview,hull,(255,255,100))
                        area_arr.sort()
                        #print area_arr
                        #Do initial calibration then checking of the target
                        App.check_obj(self,area_arr,ind)
                        winname = 'Focus' + str(ind)
                        #cv2.imshow(winname,preview)
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