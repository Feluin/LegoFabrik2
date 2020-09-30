import time

import cv2
import numpy as np


class LineTracking:
    """
    Control instance for line tracking.
    """

    def track_line(self, image):
        """
        Analyses the image for black line.

        :param image: image to analyse
        """
        # Resizes given image to analyse only bottom third and central third of the screen
        height, width, _ = image.shape
        custom_height_start = height - 160
        custom_width_start = int((width - 320) / 2)
        custom_width_end = int((width - 320) / 2 + 320)
        resized = image[custom_height_start:height,
                        custom_width_start:custom_width_end]

        # Transforms the resized image to extract the possible black line
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(
            dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Searches results for possible black line
        if len(contours) > 0:
            contours_first = contours[0]
            len_contours = len(contours_first[:, 0])

            highP = contours_first[int(len_contours / 2)]
            lowP = contours_first[0]

            # Return coordinates from detected black line
            return ((highP[0][0], highP[0][1] + 300, lowP[0][0], lowP[0][1] + 300), image)

        else:
            return (None, None)


if __name__ == '__main__':
    lt = LineTracking()
    coords, _ = lt.track_line()
    print(coords)
