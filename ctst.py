import io
import random
import picamera
from PIL import Image
import cv2
import numpy as np

def detect_motion(camera):
    global prior_image
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    stream.seek(0)
    current_image = Image.open(stream)
    img = cv2.cvtColor(np.asarray(current_image), cv2.COLOR_RGB2BGR)
    cv2.imshow('Here',img)
    cv2.waitKey(0)
    # Compare current_image to prior_image to detect motion. This is
    # left as an exercise for the reader!
    result = True
    # Once motion detection is done, make the prior image the current
    return result

def write_video(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it
    # simultaneously
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
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(1)
            if detect_motion(camera):
                print('Motion detected!')
                # As soon as we detect motion, split the recording to
                # record the frames "after" motion
                camera.split_recording('after.h264')
                # Write the 10 seconds "before" motion to disk as well
                write_video(stream)
                # Wait until motion is no longer detected, then split
                # recording back to the in-memory circular buffer
                if detect_motion(camera):
                    camera.wait_recording(7)
                print('Motion stopped!')
                camera.split_recording(stream)
                break
            break
    finally:
        camera.stop_recording()