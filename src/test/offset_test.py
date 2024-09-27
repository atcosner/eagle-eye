import cv2
import imutils
from pathlib import Path

from src.definitions.ornithology_form_v8 import TOP_REGION, BOTTOM_HALF_FIELDS, BOTTOM_HALF_Y_OFFSET


if __name__ == '__main__':
    resource_path = Path.cwd() / '..' / '..' / 'forms'

    reference_img = cv2.imread(str(resource_path / 'production' / 'kt_field_form_v8.png'))

    # Draw bounding boxes on the fields
    for field in TOP_REGION + BOTTOM_HALF_FIELDS:
        regions = []
        if 'region' in field._fields:
            regions.append(field.region)
        if 'regions' in field._fields:
            regions.extend(field.regions)
        if 'options' in field._fields:
            for option in field.options:
                regions.append(option.region)
                if option.text_region is not None:
                    regions.append(option.text_region)
        if 'text_region' in field._fields:
            regions.append(field.text_region)
        if 'checkbox_region' in field._fields:
            regions.append(field.checkbox_region)

        for region in regions:
            color = (232, 235, 52) if region.y > 944 else (36, 255, 12)
            cv2.rectangle(
                reference_img,
                (region.x, region.y),
                (region.x + region.width, region.y + region.height),
                color,
                2,
            )

    cv2.imshow("Image Alignment Overlay", imutils.resize(reference_img, width=900))
    cv2.waitKey(0)
