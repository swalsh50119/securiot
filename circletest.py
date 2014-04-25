import io
import random
import picamera
import cv2


def write_now():
    data = np.fromstring(stream.getvalue(),dtype=np.uint8)
    img = cv2.imdecode(data,1)
    #img = stream.seek(0)
    cv2.imshow('Work plz',img)
    cv2.waitkey(0)
    cv2.destroyAllWindows()
    # Randomly return True (like a fake motion detection routine)
    return 0==0

def write_video(stream):
    print('Writing video!')
    with stream.lock:
        # Find the first header frame in the video
        for frame in stream.frames:
            if frame.header:
                stream.seek(frame.position)
                break
        # Write the rest of the stream to disk
        with io.open('motion.h264', 'wb') as output:
            output.write(stream.read())

with picamera.PiCamera() as camera:
    camera.resolution = (640,480)
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(1)
            if write_now():
                # Keep recording for 5 seconds and only then write the
                # stream to disk
                #camera.wait_recording(5)
                #write_video(stream)
                print "Done writing"
                break
            break
    finally:
        camera.stop_recording()