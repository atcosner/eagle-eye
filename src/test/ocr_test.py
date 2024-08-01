import pytesseract
import cv2
import imutils
from pathlib import Path
from typing import NamedTuple

from src.test.align_images import align_images


class BoxBounds(NamedTuple):
    # Top Left
    x: int
    y: int
    width: int
    height: int


class OcrField(NamedTuple):
    name: str
    region: BoxBounds
    segment: str


OCR_FIELDS = [
    # OcrField(name='KT #', region=BoxBounds(x=248, y=140, width=125, height=37), segment='7'),
    OcrField(name='Locality', region=BoxBounds(x=281, y=191, width=804, height=31), segment='7'),
    # OcrField(name='Species', region=BoxBounds(x=287, y=267, width=686, height=31), segment='7'),
    # OcrField(name='Habitat', region=BoxBounds(x=248, y=303, width=1026, height=35), segment='7'),
    # OcrField(name='Collection Date', region=BoxBounds(x=301, y=339, width=433, height=33), segment='7'),
]


def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


if __name__ == '__main__':
    resource_path = Path.cwd() / '..' / '..' / 'forms'

    # Load the dev and production images
    test_img = cv2.imread(str(resource_path / 'production' / 'ku_collection_form_1_top.png'))
    reference_img = cv2.imread(str(resource_path / 'production' / 'ku_collection_form_template_top.png'))

    # Align them
    aligned_img = align_images(test_img, reference_img, show_matches=False)

    # initialize a results list to store the document OCR parsing results
    print("[INFO] OCR'ing document...")
    parsingResults = []

    # loop over the locations of the document we are going to OCR
    for field in OCR_FIELDS:
        # extract the OCR ROI from the aligned image
        roi = aligned_img[field.region.y:field.region.y + field.region.height, field.region.x:field.region.x + field.region.width]

        # OCR the ROI using Tesseract
        rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        thresh = cv2.GaussianBlur(rgb, (3,3), 0)
        final = cv2.copyMakeBorder(thresh, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))
        text = pytesseract.image_to_string(final, lang='eng', config=f'--psm {field.segment}')
        #print(f'{field.name}: {text}')
        cv2.imshow(field.name, final)

        # break the text into lines and loop over them
        for line in text.split("\n"):
            # if the line is empty, ignore it
            if len(line) == 0:
                continue

            # update our parsing results dictionary with the OCR'd
            # text if the line is *not* empty
            parsingResults.append((field, line))

    # initialize a dictionary to store our final OCR results
    results = {}
    # loop over the results of parsing the document
    for (loc, line) in parsingResults:
        # grab any existing OCR result for the current ID of the document
        r = results.get(loc.name, None)
        # if the result is None, initialize it using the text and location
        # namedtuple (converting it to a dictionary as namedtuples are not
        # hashable)
        if r is None:
            results[loc.name] = (line, loc._asdict())
        # otherwise, there exists an OCR result for the current area of the
        # document, so we should append our existing line
        else:
            # unpack the existing OCR result and append the line to the
            # existing text
            (existingText, loc) = r
            text = "{}\n{}".format(existingText, line)
            # update our results dictionary
            results[loc["name"]] = (text, loc)

    # loop over the results
    for (locID, result) in results.items():
        # unpack the result tuple
        (text, loc) = result
        # display the OCR result to our terminal
        print(loc["name"])
        print("=" * len(loc["name"]))
        print("{}\n\n".format(text))
        # extract the bounding box coordinates of the OCR location and
        # then strip out non-ASCII text so we can draw the text on the
        # output image using OpenCV
        (x, y, w, h) = (loc["region"].x, loc["region"].y, loc["region"].width, loc["region"].height)
        clean = cleanup_text(text)
        # draw a bounding box around the text
        cv2.rectangle(aligned_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # loop over all lines in the text
        for (i, line) in enumerate(text.split("\n")):
            # draw the line on the output image
            startY = y + (i * 70) + 40
            cv2.putText(aligned_img, line, (x, startY),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 5)

    # show the input and output images, resizing it such that they fit
    # on our screen
    # cv2.imshow("Input", imutils.resize(test_img, width=700))
    # cv2.imshow("Output", imutils.resize(aligned_img, width=700))
    cv2.waitKey(0)
