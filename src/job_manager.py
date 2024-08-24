import logging
import uuid
from pathlib import Path
from tempfile import mkdtemp

from .job import Job, HtmlJobInfo

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, reference_image: Path):
        self.job_map: dict[uuid.UUID, Job] = {}
        self.reference_image: Path = reference_image

        self.working_dir: Path = Path(mkdtemp())
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
