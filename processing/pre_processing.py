import cv2
from pathlib import Path

from . import RESOURCES_PATH


def grayscale_image(image_path: Path) -> Path:
    assert image_path.exists()

    image = cv2.imread(str(image_path))
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite()
