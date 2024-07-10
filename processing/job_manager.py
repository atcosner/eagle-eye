import logging
from pathlib import Path
from tempfile import mkdtemp

from .job import Job

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self):
        self.job_map: dict[str, Job] = {}

        self.working_dir: Path = Path(mkdtemp())
        logger.info(f'JobManager working directory: {self.working_dir}')

    def create_job(self, job_id: str) -> Job:
        self.job_map[job_id] = Job(parent_directory=self.working_dir, job_id=job_id)
        return self.job_map[job_id]
