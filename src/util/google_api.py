import base64
import cv2
import datetime
import logging
import numpy as np
import requests
import subprocess

from .settings import SettingsManager
from .types import BoxBounds

logger = logging.getLogger(__name__)

MAX_API_ATTEMPTS = 3


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
        settings.google_api_update_date = datetime.date.today()
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


def update_session_config(session: requests.Session) -> requests.Session:
    settings = SettingsManager()
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
) -> str | None:
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

    attempts = 0
    while attempts < MAX_API_ATTEMPTS:
        logger.debug(f'API OCR attempt: {attempts}')

        result = session.post(
            'https://vision.googleapis.com/v1/images:annotate',
            json=data_payload,
        )
        try:
            result.raise_for_status()
            # logger.debug(result.json())
            break
        except requests.exceptions.HTTPError as e:
            attempts += 1

            # If we got unauthorized, try updating the access token
            if e.response.status_code == 401:
                logger.info('API Authentication failed, updating acces token and retrying')
                save_api_settings()
                update_session_config(session)
            else:
                if attempts < MAX_API_ATTEMPTS:
                    logger.exception('API call failed, retrying')
                else:
                    # TODO: Handle a None return at the call sites
                    return None

    ocr_string: str | None = None
    for response in result.json()['responses']:
        if 'fullTextAnnotation' in response:
            ocr_string = response['fullTextAnnotation']['text']

    # Clean up the string
    if ocr_string is not None:
        ocr_string = ocr_string.strip().replace('\n', ' ')

    # logger.info(f'Detected: "{ocr_string}"')
    return ocr_string if ocr_string is not None else ''
