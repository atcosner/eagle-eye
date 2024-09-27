import cv2
import imutils
import numpy as np
from pathlib import Path


def locate_alignment_marks(test_image) -> None:
    gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.imshow('Threshold', imutils.resize(threshold, width=500))
    cv2.waitKey(0)

    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    matched = 0
    for c in contours:
        x, y, width, height = cv2.boundingRect(c)
        side_ratio = height / width

        contour_roi = threshold[y:y + height, x:x + width]
        white_pixels = cv2.countNonZero(contour_roi)
        color_ratio = white_pixels / (height * width)

        if (0.9 < side_ratio < 1.1) and (color_ratio < 0.2):
            print(f'{side_ratio:.2f} | {color_ratio:.2f}')
            # print(contour_roi)
            cv2.rectangle(test_image, (x, y), (x + width, y + height), (36, 255, 12), 3)
            matched += 1

    print(matched)
    cv2.imshow('Contours', imutils.resize(test_image, width=500))
    cv2.waitKey(0)

    # orb = cv2.ORB_create(100)
    # (test_keypoints, test_features) = orb.detectAndCompute(threshold, mask)
    # test1 = cv2.drawKeypoints(threshold, test_keypoints, 0, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # cv2.imshow('Test', imutils.resize(test1, width=500))
    # cv2.waitKey(0)


if __name__ == '__main__':
    resource_path = Path.cwd() / '..' / '..' / 'forms'

    test_img = cv2.imread(str(resource_path / 'dev' / 'test_kt_form__blank_big.jpg'))
    locate_alignment_marks(test_img)
