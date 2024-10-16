import cv2
import imutils

from src.forms import SUPPORTED_FORMS
from src.definitions.util import BoxBounds


def get_box_bounds(bounds: list[BoxBounds], obj) -> None:
    if not hasattr(obj, '__dict__'):
        return

    for key, value in vars(obj).items():
        # Throw out callables and dunder functions
        if callable(value) or key.startswith('__'):
            continue

        if isinstance(value, BoxBounds):
            bounds.append(value)
        else:
            get_box_bounds(box_bounds, value)


if __name__ == '__main__':
    for form in SUPPORTED_FORMS:
        box_bounds = []
        reference_img = cv2.imread(str(form.path))
        height = reference_img.shape[0]

        for fields in form.regions.values():
            for field in fields:
                get_box_bounds(box_bounds, field)

        for bounds in box_bounds:
            color = (232, 235, 52) if bounds.y > (height/2) else (36, 255, 12)
            cv2.rectangle(
                reference_img,
                (bounds.x, bounds.y),
                (bounds.x + bounds.width, bounds.y + bounds.height),
                color,
                2,
            )

        cv2.imshow(form.name, imutils.resize(reference_img, width=900))
        cv2.waitKey(0)
