import subprocess

from .util import ApiSettings


def _read_api_settings() -> ApiSettings:
    # Read project ID and access token through the gcloud CLI
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

    return ApiSettings(
        project_id=project_id,
        access_token=access_token,
    )


API_SETTINGS = _read_api_settings()
