import subprocess

from .settings import SettingsManager


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
