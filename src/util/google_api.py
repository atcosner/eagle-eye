import base64
import cv2
import logging
import numpy as np
import requests
import subprocess

from .settings import SettingsManager
from .types import BoxBounds

logger = logging.getLogger(__name__)


def save_api_settings() -> None:
    # TODO: This assumes that Google Cloud CLI has been set up
    project_id = subprocess.run(
        'gcloud config get-value project',
        check=True,
        capture_output=True,
        shell=True,
        text=True,
    ).stdout.strip()
    access_token = subprocess.run(
        'gcloud auth print-access-token',
        check=True,
        capture_output=True,
        shell=True,
        text=True,
    ).stdout.strip()

    with SettingsManager() as settings:
        settings.google_project_id = project_id
        settings.google_access_token = access_token


def open_api_session() -> requests.Session:
    settings = SettingsManager()

    session = requests.Session()
    session.headers.update(
        {
            'Authorization': f'Bearer {settings.google_access_token}',
            'x-goog-user-project': settings.google_project_id,
        }
    )
    return session


def ocr_text_region(
        session: requests.Session,
        image: np.ndarray | None = None,
        region: BoxBounds | None = None,
        roi: np.ndarray | None = None,
        add_border: bool = False,
) -> str:
    if roi is None:
        assert image is not None
        assert region is not None
        roi = image[region.y:region.y + region.height, region.x:region.x + region.width]

    if add_border:
        roi = cv2.copyMakeBorder(roi, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))

    _, buffer = cv2.imencode('.jpg', roi)
    encoded_bytes = base64.b64encode(buffer.tobytes()).decode('ascii')

    # https://cloud.google.com/vision/docs/ocr
    data_payload = {
        'requests': [
            {
                'image': {
                    'content': encoded_bytes,
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                    }
                ],
                'imageContext': {
                    'languageHints': [
                        'en-t-i0-handwrit',
                    ],
                },
            },
        ],
    }

    result = session.post(
        'https://vision.googleapis.com/v1/images:annotate',
        json=data_payload,
    )
    result.raise_for_status()
    logger.debug(result.json())

    ocr_string: str | None = None
    for response in result.json()['responses']:
        if 'fullTextAnnotation' in response:
            ocr_string = response['fullTextAnnotation']['text']

    # Clean up the string
    if ocr_string is not None:
        ocr_string = ocr_string.strip().replace('\n', ' ')

    logger.info(f'Detected: "{ocr_string}"')
    return ocr_string if ocr_string is not None else ''
