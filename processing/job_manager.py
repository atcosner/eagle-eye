import logging
import uuid
from pathlib import Path
from tempfile import mkdtemp

from .job import Job, HtmlJobInfo

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self):
        self.job_map: dict[uuid.UUID, Job] = {}

        self.working_dir: Path = Path(mkdtemp())
        logger.info(f'JobManager working directory: {self.working_dir}')

    def get_job(self, job_id: uuid.UUID) -> Job | None:
        return self.job_map.get(job_id, None)

    def get_html_job_list(self) -> list[HtmlJobInfo]:
        return [job.to_html_info() for job in self.job_map.values()]

    def create_job(self, job_id: str) -> Job:
        job_uuid = uuid.UUID(job_id)
        self.job_map[job_uuid] = Job(parent_directory=self.working_dir, job_id=job_uuid)
        return self.job_map[job_uuid]