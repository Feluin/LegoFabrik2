""" Contains the `VisionController` class to handle line following. """

# Import system libraries
import os
import time

# Import third-party libraries
import cv2
import numpy as np


class VisionController:
    """ This class handles line following with the Raspberry Pi Camera.
    If there is only one camera on the system `video_source_index` can be `0`
    (by default). """

    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240

    def __init__(self, framerate=20, video_source_index=0):
        self.camera = cv2.VideoCapture(video_source_index)
        if not self.camera.isOpened():  # if no camera found
            raise Exception('Video not available')

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,
                        VisionController.CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,
                        VisionController.CAMERA_HEIGHT)
        # Set with calculate_current_position() during loop()
        self.current_position = 0
        # Used to read the camera in the correct framerate
        # Contains the last time of the process in ms
        self.last_frame_time = 0
        # Desired fps
        self.framerate = framerate
        # Template for stop sign (read as gray image -> improves performance)
        self.template = cv2.imread(os.path.join('trucklib', 'template.jpg'), 0)
        self.template_width, self.template_heigth = self.template.shape[:2]

    def __canny(self, image):
        """ Performes a blur on the grayed image and detects edges. """

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 2)
        canny = cv2.Canny(blur, 50, 100)
        return canny

    def __region_of_interest(self, image):
        """ Removes all found edges outside of the region of interest. """

        # The polygon is a little bit over the left and right (20) to have a
        # bigger region of interest in the lower part of the image.
        polygons = np.array(
            [[(-20, VisionController.CAMERA_HEIGHT - 1),
              (VisionController.CAMERA_WIDTH + 20,
               VisionController.CAMERA_HEIGHT - 1),
              (int(VisionController.CAMERA_WIDTH / 2), 0)]])
        mask = np.zeros_like(image)  # Create empty image with same shape
        cv2.fillPoly(mask, polygons, 255)  # Fill empty image with roi
        masked_image = cv2.bitwise_and(image, mask)  # Remove everything else
        return masked_image

    def __calculate_current_position(self, lines):
        """ This function calculates the point, where to drive to.
        The center of the image is `0`.
        Distance to the left is in pixels and negative.
        Distance to the right is in pixels and positive. """

        x_sum = 0
        x_num = 0
        if lines is not None:
            for line in lines:
                x1, _, _, _ = line.reshape(4)
                x_sum += x1
                x_num += 1
            return int(x_sum / x_num)  # Using the average
        return self.current_position  # If no lines found make no change

    def __display_lines(self, image, lines, rectangle):
        """ This function takes the `lines` parameter and displays them on a
        black background with the size of `image`.
        The `rectangle` parameter is a tuple which can be null to display
        a rectangle around the found stop sign.
        The returned line_image should be combined later on. """

        line_image = np.zeros_like(image)
        # Draw lines
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 4)

        # Draw a point at the current position (in blue)
        line_image = cv2.circle(
            line_image, (self.current_position, 20), 5, (255, 0, 0), -1)

        # Draw a rectangle around the stop-sign if it is found
        if rectangle is not None:
            cv2.rectangle(line_image, rectangle[0], rectangle[1], 255, 3)

        return line_image

    def __detect_stop_sign(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(gray, self.template, cv2.TM_SQDIFF)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)

        # Threshold for detecting stop sign in the lower part (>120px)
        if min_val < 5000000 and min_loc[1] > 120:
            # Returns a tuple ((X1, Y1), (X2, Y2))
            return (min_loc,
                    (min_loc[0] + self.template_width,
                     min_loc[1] + self.template_heigth))
        return None

    def ready(self):
        """ This function returns true if the next frame should be read to
        achive the desired framerate. """

        # Current process time in milliseconds
        process_ms = time.process_time() * 1000
        lft = self.last_frame_time  # short for last frame time for readability

        if (process_ms - lft) > (1000 / self.framerate):
            if (process_ms - lft) > (1000 / self.framerate * 1.1):
                print('Could not sustain framerate. Current FPS: '
                      + str(1000 / (process_ms - lft)))

            self.last_frame_time = process_ms
            return True
        return False

    def loop(self):
        """ This function should be called every loop of the main class
        after checking ready(). It handles the line following and
        thus should be called very often and periodically. """

        ret, input_image = self.camera.read()
        if not ret:  # If no image could be read
            return None, None, 0

        input_image_copy = input_image.copy()
        rect_stop = self.__detect_stop_sign(input_image_copy)
        should_stop = False if rect_stop is None else True
        # canny_image is an image with detected edges
        canny_image = self.__canny(input_image_copy)
        # limit to region_of_interest()
        cropped_image = self.__region_of_interest(canny_image)
        # line detection using the HoughLinesP-Algorithm
        lines = cv2.HoughLinesP(
            cropped_image, 1, np.pi / 180, 25, np.array([]), 50, 30)
        self.current_position = self.__calculate_current_position(lines)
        line_image = self.__display_lines(input_image_copy, lines, rect_stop)
        combined_image = cv2.addWeighted(input_image, 0.8, line_image, 1, 1)
        # Mapping the position to the steering unit -1 to 1 for compatibility
        return_position = np.interp(self.current_position,
                                    [0, VisionController.CAMERA_WIDTH - 1],
                                    [-1, 1])

        return input_image, combined_image, return_position, should_stop
