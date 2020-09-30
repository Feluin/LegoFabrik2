import time

import cv2
import imutils
import numpy as np


class ObjectDetection:
    """
    Control instance for basic object detection.
    """

    def __init__(self):
        pass

    def detect(self, image, cascade: str):
        """
        Analyses the given image for the occurence of the given cascade.

        :param image:   image to analyse
        :param cascade: list with border points/vertices (or a trained classifier)
        """
        cascade = cv2.CascadeClassifier(cascade)

        if image != None:
            # Converts the color range of the image to gray-tone
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Searches classifier in the gray-image
            objects = cascade.detectMultiScale(gray, 1.1, 3)

            return objects

        else:
            print("frame is invalid")

    def detect_geometric_form(self, cascade):
        """
        Analyses the given cascade for geometric form.

        :param cascade: list with border points/vertices
        """
        shape = "unidentified"
        peri = cv2.arcLength(cascade, True)
        approx = cv2.approxPolyDP(cascade, 0.04 * peri, True)

        # If the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"

        # If the shape has 4 vertices, it is either a square or a rectangle
        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

        # If the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"

        # Otherwise, we assume the shape is a circle
        else:
            shape = "circle"

        return shape

    def detect_parking_slot(self, image):
        """
        Analyses the image for red rectangle (parking spot).

        :param image: image to analyse
        """
        # Transform the image to extract the possible parking spot
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create red filter mask
        lower_red = np.array([30, 150, 50])
        upper_red = np.array([255, 255, 180])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Dilate the extracted points from the red filter
        dilated = cv2.bilateralFilter(mask, 15, 75, 75)

        # Searches contours in the dilated image
        contours, _ = cv2.findContours(
            dilated, cv2.cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop over found contours
        for c in contours:
            # Get center of contour and detects shapename
            shape = self.detect_geometric_form(c)

            if shape == "square" or shape == "rectangle":
                ratio = mask.shape[0] / float(image.shape[0])
                M = cv2.moments(c)
                cx = int((M["m10"] / (M["m00"] + 1e-7)) * ratio)
                cy = int((M["m01"] / (M["m00"] + 1e-7)) * ratio)

                return True, (cy, cx)

        return False, None

    def detect_stop_sign(self, image):
        """
        Analyses the image for red stop sign.

        :param image: image to analyse
        """
        # Resize given image to analyse only bottom 80% of the screen
        height, width, _ = image.shape
        custom_height_start = height - 384
        resized = image[custom_height_start:height,
                        0:width]

        # Detect stop sign in image
        objects = self.detect(resized, '../classifiers/stop_sign.xml')
        for (x, y, w, h) in objects:

            return True, (x, y, w, h)

        return False, None

    def detect_storage_container(self, image):
        """
        Analyses the image for storage container.

        :param image: image to analyse
        """

        # Detect sorage container in image
        objects = self.detect(image, '../classifiers/palette.xml')
        for (x, y, w, h) in objects:

            return True, (x, y, w, h)

        return False, None
