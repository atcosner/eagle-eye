import logging
import os
import pandas as pd
import uuid
from pathlib import Path

from .job import Job, HtmlJobInfo

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, reference_image: Path):
        self.job_map: dict[uuid.UUID, Job] = {}
        self.reference_image: Path = reference_image

        self.working_dir: Path = Path(os.getenv('APPDATA')) / 'bi-form-processor'
        self.working_dir.mkdir(exist_ok=True)
        logger.info(f'JobManager working directory: {self.working_dir}')

    def get_job(self, job_id: uuid.UUID) -> Job | None:
        return self.job_map.get(job_id, None)

    def get_html_job_list(self) -> list[HtmlJobInfo]:
        return [job.to_html_info() for job in self.job_map.values()]

    def get_exportable_jobs(self) -> list[Job]:
        return [job for job in self.job_map.values() if job.success()]

    def create_job(self, job_id: str, job_name: str) -> Job:
        job_uuid = uuid.UUID(job_id)
        self.job_map[job_uuid] = Job(
            parent_directory=self.working_dir,
            job_id=job_uuid,
            reference_image_path=self.reference_image,
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
