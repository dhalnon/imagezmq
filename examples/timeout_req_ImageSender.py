"""timeout_req_ImageSender.py -- show use of ZMQ timeout options for restarts

A Raspberry Pi test program that uses imagezmq to send image frames from the
PiCamera continuously to a receiving program on a Mac that will display the
images as a video stream. Images are jpg compressed before sending.

One of the issues with the REQ/REP messaging pattern is that the sending program
will stall if the receiving program is stopped and restarted. This example
program show one way to use ZMQ options to restart the sender when that happens.

This image sending program uses the REQ/REP messaging pattern. It demonstrates
one way to deal with a failure to receive a REP after a REQ is sent. If the
receiving program restarts, this sending program will automatically restart.

Use the 'with_ImageHub.py' program to receive the images on the Mac. Brief
test instructions are in that program: with_ImageHub.py. Stop the program and
restart it. It should resume receiving images after it is restarted.

"""

import cv2
import sys
import time
import socket
import imagezmq
import traceback
from imutils.video import VideoStream

# use either of the formats below to specifiy address of display computer
sender = imagezmq.ImageSender(connect_to='tcp://jeff-macbook:5555')
# sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.190:5555')

rpi_name = socket.gethostname()  # send RPi hostname with each image
picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 95  # 0 to 100, higher is better quality, 95 is cv2 default
try:
    while True:  # send images as stream until Ctrl-C
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        reply_from_mac = sender.send_jpg(rpi_name, jpg_buffer)
        # above line shows how to capture REP reply text from Mac
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    if 'sender' in locals():
        sender.close()
    picam.stop()  # stop the camera thread
    sys.exit()
