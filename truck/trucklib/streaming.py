""" This file contains a class used for streaming a cv2 image to a server. """

# Import system libaries
import base64

# Import third-party libaries (e.g. OpenCV 2 and ZeroMQ)
import cv2
import zmq


class StreamingController:
    """ Helps to send a cv2 image to a server running the
    ../streaming_server.py """

    def __init__(self):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.PUB)

    def connect(self, target_url):
        """ Connects to a running server code (in the class description).
        For `target_url` an example value is `tcp://192.168.1.2:5555`.
        Make sure to check firewall restrictions on the server side! """

        self.footage_socket.connect(target_url)

    def loop(self, image):
        """ The function should be called every loop of the main class.
        This ensures that each frame will be sent to the server. """

        _, buffer = cv2.imencode('.jpg', image)  # Using compression
        jpg_as_text = base64.b64encode(buffer)
        self.footage_socket.send(jpg_as_text)
