import logging
import os
import pandas as pd
import uuid
from pathlib import Path

from src.definitions.forms import ReferenceForm, SUPPORTED_FORMS

from .job import Job, HtmlJobInfo

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self):
        self.job_map: dict[uuid.UUID, Job] = {}

        self.working_dir: Path = Path(os.getenv('APPDATA')) / 'kubi-form-processor'
        self.working_dir.mkdir(exist_ok=True)
        logger.info(f'JobManager working directory: {self.working_dir}')

    def get_supported_forms(self) -> list[ReferenceForm]:
        return SUPPORTED_FORMS

    def get_job(self, job_id: uuid.UUID) -> Job | None:
        return self.job_map.get(job_id, None)

    def get_html_job_list(self) -> list[HtmlJobInfo]:
        return [job.to_html_info() for job in self.job_map.values()]

    def get_exportable_jobs(self) -> list[Job]:
        return [job for job in self.job_map.values() if job.succeeded()]

    def create_job(self, job_id: str, job_name: str, reference_form_name: str) -> Job:
        # Find the reference form
        reference_form: ReferenceForm | None = None
        for form in SUPPORTED_FORMS:
            if form.name == reference_form_name:
                reference_form = form

        if reference_form is None:
            raise RuntimeError(f'Failed to find a reference form with name: "{reference_form_name}"')

        job_uuid = uuid.UUID(job_id)
        self.job_map[job_uuid] = Job(
            parent_directory=self.working_dir,
            job_id=job_uuid,
            reference_form=reference_form,
            job_name=job_name,
        )
        return self.job_map[job_uuid]

    def export_jobs(self, job_ids: list[uuid.UUID]) -> Path:
        dataframes = []
        for job_id in job_ids:
            if job := self.get_job(job_id):
                dataframes.append(job.export_results())
            else:
                logger.warning(f'Did not find job with id: {job_id}')

        excel_path = self.working_dir / 'export.xlsx'
        merged_df = pd.concat(dataframes).reset_index()
        merged_df.to_excel(excel_path)

        return excel_path
