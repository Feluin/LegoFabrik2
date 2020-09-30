""" This file contains a basic server to receive the camera stream from the
truck. This should be executed on a pc on the same network as the Raspberry Pi.
Make sure the port on the server is not blocked, because of a firewall (e.g.
Windows Firewall). Inspired by https://stackoverflow.com/a/51718862. """

# Import libraries (e.g. OpenCV 2 and ZeroMQ)
import base64
import cv2
import zmq
import numpy as np

# Define constants
CONTEXT = zmq.Context()
FOOTAGE_SOCKET = CONTEXT.socket(zmq.SUB)
FOOTAGE_SOCKET.bind('tcp://*:5555')  # Use TCP on local port 5555
FOOTAGE_SOCKET.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

while True:
    try:
        FRAME = FOOTAGE_SOCKET.recv_string()
        IMAGE = base64.b64decode(FRAME)
        NUMPY_IMAGE = np.fromstring(IMAGE, dtype=np.uint8)
        SOURCE_OF_IMAGE = cv2.imdecode(NUMPY_IMAGE, 1)
        cv2.imshow("Stream", SOURCE_OF_IMAGE)
        cv2.waitKey(1)  # Used to keep the image-window opened

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
